import geopandas as gpd
from sqlalchemy import create_engine
from geoalchemy2 import Geometry

# Database connection parameters
DB_NAME = "gis"
DB_USER = "shubhanshub"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# Path to the GeoPackage file
GPKG_PATH = r"C:\Users\shubh\Downloads\OGIM_v2.5.1.gpkg"

def load_pipelines_to_postgres():
    try:
        # Read the GeoPackage layer with filters applied
        gdf = gpd.read_file(
            GPKG_PATH,
            layer="Oil_Natural_Gas_Pipelines",
            where="STATE_PROV = 'NEW MEXICO'"
        )

        # Create PostgreSQL connection
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        # Write data to PostgreSQL with PostGIS geometry
        gdf.to_postgis(
            name="new_mexico_pipelines",  # Table name
            con=engine,
            if_exists="replace",
            index=False,
            dtype={"geometry": Geometry("MULTILINESTRING", srid=4326)}
        )

        print("Data successfully loaded into PostgreSQL!")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
if __name__ == "__main__":
    load_pipelines_to_postgres()
