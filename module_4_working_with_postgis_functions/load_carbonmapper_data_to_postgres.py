import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db_table(conn) -> None:
    """Create the necessary table if it doesn't exist"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS public;

            CREATE TABLE IF NOT EXISTS public.carbonmapper_plumes (
                id UUID PRIMARY KEY,
                plume_id VARCHAR(255),
                gas VARCHAR(50),
                coordinates_3857 GEOMETRY(Point, 3857),
                coordinates GEOMETRY(Point, 4326),
                scene_id UUID,
                scene_timestamp TIMESTAMP,
                instrument VARCHAR(50),
                platform VARCHAR(100),
                emission_auto FLOAT,
                emission_uncertainty_auto FLOAT,
                plume_bounds FLOAT[],
                collection VARCHAR(100),
                cmf_type VARCHAR(50),
                sector VARCHAR(50),
                status VARCHAR(50),
                hide_emission BOOLEAN,
                cm_published_date TIMESTAMP,
                eog_ingest_date TIMESTAMP,
                data_source VARCHAR(50),
                plume_png TEXT,
                plume_rgb_png TEXT,
                plume_tif TEXT,
                rgb_png TEXT,
                vast_plume_url TEXT,
                raw_data JSONB
            )
        """)
        conn.commit()


def get_plume_data(offset: int = 0, limit: int = 9000) -> Dict[str, Any]:
    """Fetch data from Carbon Mapper API with pagination and filtering"""
    url = "https://api.carbonmapper.org/api/v1/catalog/plumes/annotated"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://data.carbonmapper.org',
        'referer': 'https://data.carbonmapper.org/'
    }

    # Calculate date range (last 180 days)
    yesterday = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    today = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    params = {
        'limit': limit,
        'offset': offset,
        'bbox': [-126.7568, 10.2448, -62.5152, 60.1746],  # North America bbox
        'datetime': f"{yesterday}/{today}",
        'sort': 'desc'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def insert_plume_data_batch(conn, plumes: List[Dict[str, Any]]) -> None:
    """Insert multiple plume records into the database using batch processing"""
    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datasource = "carbonmapper"

    with conn.cursor() as cur:
        for plume in plumes:
            # Check if record already exists
            cur.execute("SELECT 1 FROM public.carbonmapper_plumes WHERE id = %s", (plume["id"],))
            if cur.fetchone():
                continue

            coords = plume['geometry_json']['coordinates']
            point_wkt = f'POINT({coords[0]} {coords[1]})'

            cur.execute("""
                INSERT INTO public.carbonmapper_plumes (
                    id, plume_id, gas, coordinates_3857, coordinates, scene_id, 
                    scene_timestamp, instrument, platform, emission_auto,
                    emission_uncertainty_auto, plume_bounds, collection, cmf_type, 
                    sector, status, hide_emission, cm_published_date, eog_ingest_date,
                    data_source, plume_png, plume_rgb_png, plume_tif, rgb_png,
                    raw_data
                ) VALUES (
                    %s, %s, %s, 
                    ST_Transform(ST_GeomFromText(%s, 4326), 3857),
                    ST_GeomFromText(%s, 4326),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, (
                plume['id'],
                plume['plume_id'],
                plume['gas'],
                point_wkt,
                point_wkt,
                plume['scene_id'],
                plume['scene_timestamp'],
                plume['instrument'],
                plume['platform'],
                plume['emission_auto'],
                plume['emission_uncertainty_auto'],
                plume['plume_bounds'],
                plume['collection'],
                plume['cmf_type'],
                plume['sector'],
                plume['status'],
                plume.get('hide_emission'),
                plume['published_at'],
                datetime_now,
                datasource,
                plume['plume_png'],
                plume['plume_rgb_png'],
                plume['plume_tif'],
                plume['rgb_png'],
                Json(plume)
            ))

        conn.commit()


def main():
    # Database connection parameters
    db_params = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432'
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)

        # Create table if it doesn't exist
        create_db_table(conn)

        offset = 0
        total_processed = 0
        batch_size = 9000  # Number of records to fetch per request

        while True:
            # Fetch batch of data from API
            logger.info(f"Fetching records with offset {offset}...")
            response_data = get_plume_data(offset=offset, limit=batch_size)

            items = response_data['items']
            if not items:
                break

            # Process the batch
            insert_plume_data_batch(conn, items)

            total_processed += len(items)
            logger.info(f"Processed {len(items)} records. Total processed: {total_processed}")

            # Check if we've reached the end
            if len(items) < batch_size:
                break

            offset += batch_size

            # Add a small delay to avoid overwhelming the API
            time.sleep(1)

        logger.info(f"Successfully processed all plume data. Total records: {total_processed}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()