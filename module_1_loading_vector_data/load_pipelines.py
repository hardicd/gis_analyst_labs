import geopandas as gpd
from sqlalchemy import create_engine

# Database connection parameters
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# function to load the data to postgres
def load_wells_to_postgres():
    # Read the filtered GeoPackage data
    gdf = gpd.read_file(
        "/Users/philipahrens/Downloads/OGIM_v2.5.1.gpkg",
        layer='Oil_Natural_Gas_Pipelines', # layer name
        mask=None,
        where="STATE_PROV = 'NEW MEXICO'" # filter criteria
    )

    # Create PostgreSQL connection
    engine = create_engine(
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}' # connection string
    )

    # Write to PostgreSQL with PostGIS geometry
    gdf.to_postgis(
        name='Oil_Natural_Gas_Pipelines', # table name
        con=engine,
        if_exists='replace',
        index=False,
        dtype={'geometry': 'geometry'}
    )
# run the function
if __name__ == "__main__":
    load_wells_to_postgres()