-- First query: Add the new column
ALTER TABLE new_mexico_producing_wells 
ADD COLUMN closest_carbonmapper_plume text;

-- Second query: Update the values
WITH closest_plumes AS (
  SELECT DISTINCT ON (w."OGIM_ID")
    w."OGIM_ID"::int8 as well_id,
    CONCAT(w."FAC_NAME", ' ', w."OPERATOR") as plume_info,
    ST_Distance(
      ST_Transform(w.geometry, 2877),  -- Transform to NAD83 / New Mexico East (ft) for accurate distance
      ST_Transform(p.coordinates, 2877)
    ) as distance
  FROM new_mexico_producing_wells w
  LEFT JOIN carbonmapper_plumes p
    ON ST_DWithin(
      ST_Transform(w.geometry, 2877),
      ST_Transform(p.coordinates, 2877),
      300  -- 300 feet threshold
    )
  WHERE ST_Distance(
    ST_Transform(w.geometry, 2877),
    ST_Transform(p.coordinates, 2877)
  ) <= 300
  ORDER BY w."OGIM_ID"::int8, distance
)
UPDATE new_mexico_producing_wells w
SET closest_carbonmapper_plume = cp.plume_info
FROM closest_plumes cp
WHERE w."OGIM_ID"::int8 = cp.well_id;

--Third query: select the well records that have a plume close to them
SELECT "OGIM_ID", "FAC_NAME", "OPERATOR", closest_carbonmapper_plume
FROM new_mexico_producing_wells
WHERE closest_carbonmapper_plume IS NOT NULL
ORDER BY "OGIM_ID";