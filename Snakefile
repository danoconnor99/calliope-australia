configfile: "config/default.yaml"

include: "rules/submodules.smk"
include: "rules/build_nodes.smk"
# include: "rules/land_area.smk"



# include: "rules/rooftop_cf.smk"

# include: "rules/capacities.smk"
# include: "rules/vintages_postprocessing.smk"
# include: "rules/build_atlite_cf.smk"
# include: "rules/build_weather.smk"
# include: "rules/run.smk"
# include: "rules/sync.smk"

# include: "rules/build_weather_feasibility.smk"
# include: "rules/feasibility.smk"


# SCENARIOS = [1, 2, 3, 4, 5]
# SCENARIO_LABELS = {wy: f"{wy}yrs" for wy in SCENARIOS}

# RUN_WINDOWS = {
#     1: (2011, 2015),
#     2: (2006, 2010),
#     3: (2001, 2005),
# }
# RUN_LABELS = {r: f"run{r}_{start}_{end}" for r, (start, end) in RUN_WINDOWS.items()}

# import re

# def wy_from_label(label):
#     return int(label.replace("yrs", ""))

# def run_from_label(label):
#     return int(label.split("_")[0].replace("run", ""))

# SUPPLY_FILES = [
#     "capacityfactors-rooftop-pv",
#     "capacityfactors-open-field-pv",
#     "capacityfactors-wind-offshore",
#     "capacityfactors-wind-onshore",
#     "capacityfactors-hydro-run-of-river",
#     "capacityfactors-hydro-reservoir",
#     "historic-electrified-heat",
# ]

# DEMAND_FILES = [
#     "electrified-heat",
#     "electricity",
# ]

rule all:
    message: "Calliope Dataset"
    input:
        "build/temp/shapes.parquet",
        "build/output/locations.yaml"
#         #initial weather
#         "build/temp/capacityfactors-open-field-pv.csv",
#         "build/temp/capacityfactors-wind-onshore.csv",
#         "build/temp/capacityfactors-wind-offshore.csv",
#         "build/temp/capacityfactors-hydro-reservoir.csv",
#         "build/temp/capacityfactors-hydro-run-of-river.csv",
#         "build/temp/capacityfactors-rooftop-pv.csv",
#         # nodes
#         expand("build/output/{f}", f=["nodes.yml","locations.yml"]),

#         # availability_curves outputs:
#         "build/data_tables/initial_capacity_techs_kw.csv",
#         "build/data_tables/max_capacity_techs_kw.csv",
#         "build/data_tables/investstep_series/available_initial_cap_techs.csv",
#         "build/data_tables/investstep_series/available_vintages_techs.csv",
#         "build/data_tables/investstep_series/available_vintages_transmission.csv",
#         "build/data_tables/investstep_series/investstep_resolution.csv",
#         "build/data_tables/nuclear_capacities.csv",

#         #processed weather
#         expand(
#             "models/national/timeseries/supply/scenarios/{run_label}/{wy_label}/{f}.csv",
#             run_label=RUN_LABELS.values(),
#             wy_label=SCENARIO_LABELS.values(),
#             f=SUPPLY_FILES,
#         ),
#         expand(
#             "models/national/timeseries/demand/scenarios/{run_label}/{wy_label}/{f}.csv",
#             run_label=RUN_LABELS.values(),
#             wy_label=SCENARIO_LABELS.values(),
#             f=DEMAND_FILES,
#         ),

#         # output
#         expand("data/output/model_{run_label}_{wy_label}.nc",
#             run_label=RUN_LABELS.values(),
#             wy_label=SCENARIO_LABELS.values()),


    default_target: True


