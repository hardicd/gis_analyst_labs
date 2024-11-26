# Working with PostGIS Built-in Functions

# Learning objectives:
- Running SQL scripts
- Reusing python environments
- Using PostGIS built-in functions to perform proximity queries: ST_DWithin, ST_Transform, ST_Distance


# Lab 4 instructions:
1. Install DBeaver https://dbeaver.io/download/ or use the built-in pgAdmin that comes with your postgres database installation.

2. Create a new python environment and install the required packages: geopandas, sqlalchemy, psycopg2-binary, psycopg2. Or use the one you created in module_1.

3. Change the database connection parameters in the load_carbonmapper_data_to_postgres.py script to connect to your local postgres database.

4. Run the load_carbonmapper_data_to_postgres.py script to load the CarbonMapper data to your local postgres database in the public schema. A new table called 'carbonmapper_plumes' will be created.

5. Run the SQL in the "postgis_proximity_query.sql" script that uses PostGIS functions to assign a location from the 'new_mexico_producing_wells' table we created in module_1. It uses a proximity query that’s within 300’. The script should create a new column called 'closest_carbonmapper_plume' in the 'new_mexico_producing_wells' table that is a concatenation of the 'FAC_NAME' and 'OPERATOR' fields. 

6. Take a screenshot of the results of the third query in the "postgis_proximity_query.sql" script.


# Assessment:

Copy the screenshot of the results of the third query to the assessment folder.
