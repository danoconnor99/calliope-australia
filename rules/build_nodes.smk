rule build_nodes:
    input:
        gdf="build/temp/shapes.parquet",
    output:
        nodes='build/output/nodes.yaml',
        locations='build/output/locations.yaml'
    conda:
        '../envs/geo.yaml'
    script:
        '../scripts/build_nodes.py'