#!/usr/bin/env python3
from pathlib import Path
import sys
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt

# ---------------- User settings ----------------
INPUT = "submodules/geo_boundaries/results/shapes.parquet"
DROP_LAND_NAMES = {"Ashmore and Cartier Islands", "Coral Sea Islands Territory", "Jervis Bay Territory"}
PROJECT_EPSG = 3577
GLOBAL_SEED_CAP = 3000
# ------------------------------------------------

# Get output paths from Snakemake
PARQUET = Path(snakemake.output[0])
PNG = Path(snakemake.output[1])
PARQUET.parent.mkdir(parents=True, exist_ok=True)

# small mapping: state full name -> short code used in state_id
ABBR = {
    "Australian Capital Territory": "ACT",
    "New South Wales": "NSW",
    "Northern Territory": "NT",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Victoria": "VIC",
    "Western Australia": "WA",
}

# Load data
g = gpd.read_parquet(INPUT)
g.columns = [str(c) for c in g.columns]
g = g[~g["parent_name"].isin(DROP_LAND_NAMES)].copy()
g = g.set_crs(epsg=4326).to_crs(epsg=PROJECT_EPSG)

# Generate state_id for land polygons
land_gdf = g[g["shape_class"] == "land"].copy()
# keep the full name too
land_gdf["state_name"] = land_gdf["parent_name"]
# set state_id as <CODE> using ABBR (fallback: first 3 letters uppercase)
land_gdf["state_id"] = land_gdf["state_name"].map(lambda n: ABBR.get(n, "".join(w[0] for w in str(n).split())[:3].upper()))

# EEZ rows
eez_rows = g[g["parent_subtype"].astype(str).str.contains("eez", na=False)]
if eez_rows.empty:
    raise RuntimeError("EEZ rows not found in input.")
eez_union = eez_rows.unary_union
g_noeez = g.drop(index=eez_rows.index)

# Build mapping from parent_name -> state_id and numeric part
state_map = dict(zip(land_gdf["parent_name"], land_gdf["state_id"]))
num_map = {row["parent_name"]: row["shape_id"].split(".")[1] for _, row in land_gdf.iterrows()}

# Build seed points from coastline vertices near EEZ bbox
seed_pts, seed_labels = [], []
eez_bbox = eez_union.envelope.buffer(300_000)  # 300 km buffer
for _, row in land_gdf.iterrows():
    geom = row.geometry
    if not geom.intersects(eez_bbox):
        continue
    parts = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for part in parts:
        for x, y in part.exterior.coords:
            seed_pts.append((x, y))
            seed_labels.append(row["parent_name"])

seed_pts = np.array(seed_pts)
if seed_pts.size == 0:
    raise RuntimeError("No seed points generated (check coastlines / buffer).")

# Deduplicate and cap seeds
uniq_pts, uniq_idx = np.unique(seed_pts, axis=0, return_index=True)
seed_pts = uniq_pts
seed_labels = [seed_labels[i] for i in uniq_idx]
if len(seed_pts) > GLOBAL_SEED_CAP:
    step = int(np.ceil(len(seed_pts) / GLOBAL_SEED_CAP))
    seed_pts = seed_pts[::step]
    seed_labels = seed_labels[::step]

# Compute Voronoi
vor = Voronoi(seed_pts)

# Build finite polygons
new_regions = []
center = vor.points.mean(axis=0)
radius = np.ptp(vor.points, axis=0).max() * 2

all_ridges = {}
for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
    all_ridges.setdefault(p1, []).append((p2, v1, v2))
    all_ridges.setdefault(p2, []).append((p1, v1, v2))

for p1, region_idx in enumerate(vor.point_region):
    vertices = vor.regions[region_idx]
    if all(v >= 0 for v in vertices):
        new_regions.append([vor.vertices[v].tolist() for v in vertices])
        continue
    ridges = all_ridges[p1]
    pts = []
    for p2, v1, v2 in ridges:
        if v1 < 0 or v2 < 0:
            v = v1 if v1 >= 0 else v2
            t = vor.points[p2] - vor.points[p1]
            t = t / np.linalg.norm(t)
            n = np.array([-t[1], t[0]])
            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far = vor.vertices[v] + direction * radius
            pts.extend([vor.vertices[v].tolist(), far.tolist()])
        else:
            pts.extend([vor.vertices[v1].tolist(), vor.vertices[v2].tolist()])
    poly = Polygon(pts).convex_hull
    new_regions.append(list(poly.exterior.coords))

# Clip Voronoi polygons to EEZ
polys = []
for i, region in enumerate(new_regions):
    poly = Polygon(region)
    poly_clipped = poly.intersection(eez_union)
    if not poly_clipped.is_empty:
        polys.append({"geometry": poly_clipped, "parent_name": seed_labels[i]})

vor_gdf = gpd.GeoDataFrame(polys, crs=g.crs)
vor_by_state = vor_gdf.dissolve(by="parent_name", as_index=False)
vor_by_state["shape_class"] = "maritime"
# preserve full name
vor_by_state["state_name"] = vor_by_state["parent_name"]
# set <CODE>
vor_by_state["state_id"] = vor_by_state["state_name"].map(lambda n: ABBR.get(n, "".join(w[0] for w in str(n).split())[:3].upper()))
# keep numeric-based shape_id aligned with land
vor_by_state["shape_id"] = vor_by_state["parent_name"].map(lambda n: f"AUS_marineregions.{num_map[n]}_1")
vor_by_state["country_id"] = "AUS"

# Keep only required columns (now including state_name)
vor_by_state = vor_by_state[["shape_id", "country_id", "state_id", "state_name", "shape_class", "geometry"]]
land_gdf = land_gdf[["shape_id", "country_id", "state_id", "state_name", "shape_class", "geometry"]]

# Combine land + maritime
final_gdf = pd.concat([land_gdf, vor_by_state], ignore_index=True)
final_gdf = gpd.GeoDataFrame(final_gdf, crs=g.crs)
final_gdf.to_parquet(PARQUET)

# Plot in WGS84
land_plot = final_gdf[final_gdf["shape_class"] == "land"].to_crs(4326)
mar_plot  = final_gdf[final_gdf["shape_class"] == "maritime"].to_crs(4326)
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect("equal")
mar_plot.plot(ax=ax, color="#30c7d5", linewidth=0, zorder=1)
marine_b_int = mar_plot.dissolve(by="state_id").boundary
gpd.GeoDataFrame(geometry=marine_b_int[~marine_b_int.is_empty], crs=mar_plot.crs).plot(
    ax=ax, color="#108da0", linewidth=0.9, zorder=2
)
gpd.GeoDataFrame(geometry=mar_plot.dissolve().boundary[~mar_plot.dissolve().boundary.is_empty], crs=mar_plot.crs).plot(
    ax=ax, color="#108da0", linewidth=1.2, zorder=2
)
land_plot.dissolve().plot(ax=ax, color="#1f6fb8", edgecolor="none", zorder=3)
land_plot.dissolve(by="state_id").boundary.plot(ax=ax, color="white", linewidth=0.4, zorder=4)
ax.set_title("Voronoi coastal-based EEZ allocation")
fig.tight_layout()
fig.savefig(PNG, dpi=200)
plt.close(fig)
