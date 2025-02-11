import geopandas as gpd
from sqlalchemy import create_engine
import psycopg2

# Database connection parameters
DB_NAME = "gis"
DB_USER = "shubhanshub"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to load the data to PostgreSQL
def load_wells_to_postgres():
    try:
        # Read the GeoPackage file
        gdf = gpd.read_file(
            r"C:\Users\shubh\Downloads\OGIM_v2.5.1.gpkg",  # Raw string path to avoid issues
            layer="Oil_and_Natural_Gas_Wells",  # Layer name
            where="STATE_PROV = 'NEW MEXICO' AND OGIM_STATUS = 'PRODUCING'"  # Filter criteria
        )

        # Create PostgreSQL connection
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        # Write to PostgreSQL with PostGIS geometry
        gdf.to_postgis(
            name="new_mexico_producing_wells",  # Table name
            con=engine,
            if_exists="replace",  # Replace table if it exists
            index=False,
            dtype={"geometry": "geometry"}  # Ensure geometry is correctly handled
        )

        print("Data successfully loaded into PostgreSQL!")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
if __name__ == "__main__":
    load_wells_to_postgres()
