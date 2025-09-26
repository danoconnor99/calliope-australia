module geo_boundaries:
    snakefile:
        github("calliope-project/module_geo_boundaries", path="workflow/Snakefile", tag="v0.1.3")
    config: config["module_geo_boundaries"]
    prefix: "submodules/geo_boundaries"

use rule * from geo_boundaries as module_geo_boundaries_*

use rule download_country_overture from geo_boundaries as module_geo_boundaries_download_country_overture with:
    localrule: True
use rule download_country_gadm from geo_boundaries as module_geo_boundaries_download_country_gadm with:
    localrule: True
use rule standardise_country_gadm from geo_boundaries as module_geo_boundaries_standardise_country_gadm with:
    localrule: True
use rule download_nuts from geo_boundaries as module_geo_boundaries_download_nuts with:
    localrule: True
use rule standardise_country_nuts from geo_boundaries as module_geo_boundaries_standardise_country_nuts with:
    localrule: True
use rule download_marine_eez_area from geo_boundaries as module_geo_boundaries_download_marine_eez_area with:
    localrule: True

rule filter_parquet:
    input:
        shapes="submodules/geo_boundaries/results/shapes.parquet"
    output:
        parquet="build/temp/shapes.parquet",
        png="build/temp/shapes.png"
    script:
        "../scripts/filter_shapes.py"