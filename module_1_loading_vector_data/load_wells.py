import geopandas as gpd
from sqlalchemy import create_engine

# Database connection parameters
DB_NAME = "your_database_name_here"
DB_USER = "your_pg_username_here"
DB_PASSWORD = "your_pg_password_here"
DB_HOST = "localhost"
DB_PORT = "5432"

# function to load the data to postgres
def load_wells_to_postgres():
    # Read the filtered GeoPackage data
    gdf = gpd.read_file(
        "C:/file/path/to/your/downloaded/data/here/OGIM_v2.5.1.gpkg",
        layer='Oil_and_Natural_Gas_Wells', # layer name
        mask=None,
        where="STATE_PROV = 'NEW MEXICO' AND OGIM_STATUS = 'PRODUCING'" # filter criteria
    )

    # Create PostgreSQL connection
    engine = create_engine(
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}' # connection string
    )

    # Write to PostgreSQL with PostGIS geometry
    gdf.to_postgis(
        name='new_mexico_producing_wells', # table name 
        con=engine,
        if_exists='replace',
        index=False,
        dtype={'geometry': 'geometry'}
    )
# run the function
if __name__ == "__main__":
    load_wells_to_postgres() 