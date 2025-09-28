from pathlib import Path
import geopandas as gpd
import yaml

gdf = gpd.read_parquet(snakemake.input.gdf)
gdf = gdf[gdf["shape_class"] == "land"].set_index("state_id")
if gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

centroids = gdf.geometry.centroid
gdf["lon"] = centroids.x
gdf["lat"] = centroids.y


nodes = {idx: {"available_area": None} for idx in gdf.index}
locations = {
    idx: {"latitude": float(round(row.lat, 6)), "longitude": float(round(row.lon, 6))}
    for idx, row in gdf.iterrows()
}

yaml.SafeDumper.ignore_aliases = lambda *args: True
out_nodes = Path(snakemake.output.nodes)
out_locations = Path(snakemake.output.locations)
out_nodes.parent.mkdir(parents=True, exist_ok=True)
out_nodes.write_text(yaml.safe_dump(nodes, sort_keys=False))
out_locations.write_text(yaml.safe_dump(locations, sort_keys=False))