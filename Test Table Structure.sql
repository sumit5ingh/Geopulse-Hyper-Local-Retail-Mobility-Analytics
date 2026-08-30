-- GeoPulse — Member 3: Schema & Tables
-- Day 5: Test Table Structure
-- Run against geopulse_db.retail_analytics (after schema_and_tables.sql)

USE SCHEMA geopulse_db.retail_analytics;


-- 1. STRUCTURAL CHECKS — confirm columns/types match Day 2 design

DESC TABLE distance_data;
DESC TABLE footfall_summary;

-- Row counts before loading test data (should be 0 on a fresh table)
SELECT COUNT(*) AS row_count FROM distance_data;
SELECT COUNT(*) AS row_count FROM footfall_summary;


-- 2. VALID TEST INSERTS — one normal row per table

INSERT INTO distance_data VALUES (
    '00696abc-3e18-4654-b046-796ecebd914b', 'Commuter',
    21.139401, 79.063988,
    2036.3, 2590.6, 4400.7,
    'STR001', 'Store A - Sitabuldi', 2036.3
);

INSERT INTO footfall_summary VALUES (
    'STR001', 'Store A - Sitabuldi', 'Supermarket', '2026-08-10',
    37, 2232.0, 34, 60.3
);


-- 3. EDGE CASE INSERTS — boundary values

-- Zero distance (device located exactly at the store)
INSERT INTO distance_data VALUES (
    '11111111-1111-1111-1111-111111111111', 'Resident',
    21.140000, 79.070000,
    0.0, 3500.2, 5200.9,
    'STR001', 'Store A - Sitabuldi', 0.0
);

-- Max-length name / long store name string (near VARCHAR(50) limit)
INSERT INTO footfall_summary VALUES (
    'STR002', 'Store B - Very Long Name Testing Fifty Char Limit', 'Mall',
    '2026-08-10', 0, 0.0, 0, 0.0
);

-- NULL-able fields left blank (none are declared NOT NULL currently —
-- this row checks whether that's actually the intended behavior)
INSERT INTO distance_data (device_id, persona, home_lat, home_lon)
VALUES ('22222222-2222-2222-2222-222222222222', 'Shopper', 21.15, 79.08);


-- 4. NEGATIVE TEST — this INSERT should fail (wrong data type)
-- Run separately and confirm it errors out; do not leave in prod script

-- INSERT INTO footfall_summary (store_id, total_visits) VALUES ('STR003', 'not_a_number');


-- 5. UNIQUENESS / DUPLICATE CHECKS
-- (no PK is enforced by Snowflake, so check manually)

SELECT device_id, COUNT(*) AS occurrences
FROM distance_data
GROUP BY device_id
HAVING COUNT(*) > 1;

SELECT store_id, date, COUNT(*) AS occurrences
FROM footfall_summary
GROUP BY store_id, date
HAVING COUNT(*) > 1;



-- 6. REFERENTIAL CHECK — nearest_store_id in distance_data
-- should always exist in footfall_summary.store_id

SELECT DISTINCT d.nearest_store_id
FROM distance_data d
LEFT JOIN footfall_summary f
    ON d.nearest_store_id = f.store_id
WHERE f.store_id IS NULL;
-- Expected: empty result. Any rows returned = orphaned store references.



-- 7. JOIN SANITY CHECK

SELECT
    f.store_id,
    f.store_name,
    f.total_visits,
    COUNT(d.device_id) AS devices_with_this_as_nearest
FROM footfall_summary f
LEFT JOIN distance_data d
    ON f.store_id = d.nearest_store_id
GROUP BY f.store_id, f.store_name, f.total_visits
ORDER BY f.store_id;



-- 8. AGGREGATE / RANGE SANITY CHECKS

-- Distances should be non-negative and within a plausible range for Nagpur (< ~30km)
SELECT
    MIN(distance_to_nearest_store_m) AS min_dist,
    MAX(distance_to_nearest_store_m) AS max_dist,
    AVG(distance_to_nearest_store_m) AS avg_dist
FROM distance_data;

-- Lat/lon should fall within Nagpur's rough bounding box
SELECT device_id, home_lat, home_lon
FROM distance_data
WHERE home_lat NOT BETWEEN 20.9 AND 21.3
   OR home_lon NOT BETWEEN 78.9 AND 79.3;
-- Expected: empty result. Any rows = bad/out-of-region coordinates.

-- Footfall metrics should be non-negative and unique_visitors <= total_visits
SELECT *
FROM footfall_summary
WHERE total_visits < 0
   OR unique_visitors < 0
   OR unique_visitors > total_visits;
-- Expected: empty result.


 
-- 9. CLEANUP — remove test rows once verification is done

-- DELETE FROM distance_data WHERE device_id IN (
--     '00696abc-3e18-4654-b046-796ecebd914b',
--     '11111111-1111-1111-1111-111111111111',
--     '22222222-2222-2222-2222-222222222222'
-- );
-- DELETE FROM footfall_summary WHERE store_id IN ('STR001','STR002');