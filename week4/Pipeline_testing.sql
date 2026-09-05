USE DATABASE GEOPULSE;
USE SCHEMA RETAIL_ANALYSIS;

CREATE OR REPLACE TABLE PIPELINE_TEST_RESULTS (
    TEST_NAME VARCHAR,
    TEST_RESULT VARCHAR,
    TEST_VALUE VARCHAR,
    TEST_TIMESTAMP TIMESTAMP
);

-- ============================================================
-- GEOPULSE
-- AUTOMATED PIPELINE TESTING
-- ============================================================

USE DATABASE GEOPULSE;
USE SCHEMA RETAIL_ANALYSIS;


-- ============================================================
-- CLEAR PREVIOUS RESULTS
-- ============================================================

TRUNCATE TABLE PIPELINE_TEST_RESULTS;


-- ============================================================
-- TEST 1: GPS DATA AVAILABILITY
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'GPS Data Availability',
    CASE
        WHEN COUNT(*) > 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 2: GPS EXPECTED ROW COUNT
-- Expected: 116951
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'GPS Row Count Validation',
    CASE
        WHEN COUNT(*) = 116951 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 3: NULL VALUE VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'GPS NULL Validation',
    CASE
        WHEN COUNT_IF(lat IS NULL) = 0
         AND COUNT_IF(lon IS NULL) = 0
         AND COUNT_IF(timestamp IS NULL) = 0
         AND COUNT_IF(device_id IS NULL) = 0
         AND COUNT_IF(ping_id IS NULL) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    (
        COUNT_IF(lat IS NULL)
        + COUNT_IF(lon IS NULL)
        + COUNT_IF(timestamp IS NULL)
        + COUNT_IF(device_id IS NULL)
        + COUNT_IF(ping_id IS NULL)
    )::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 4: LATITUDE VALIDATION
-- Valid range: -90 to 90
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Latitude Validation',
    CASE
        WHEN COUNT_IF(lat < -90 OR lat > 90) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(lat < -90 OR lat > 90)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 5: LONGITUDE VALIDATION
-- Valid range: -180 to 180
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Longitude Validation',
    CASE
        WHEN COUNT_IF(lon < -180 OR lon > 180) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(lon < -180 OR lon > 180)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 6: GPS ACCURACY VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'GPS Accuracy Validation',
    CASE
        WHEN COUNT_IF(gps_accuracy_m < 0) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(gps_accuracy_m < 0)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 7: DISTANCE FROM HOME VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Distance From Home Validation',
    CASE
        WHEN COUNT_IF(distance_from_home_m < 0) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(distance_from_home_m < 0)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 8: DUPLICATE PING VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Duplicate Ping ID Validation',
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM (
    SELECT ping_id
    FROM GPS_DATA
    GROUP BY ping_id
    HAVING COUNT(*) > 1
);


-- ============================================================
-- TEST 9: SEQUENCE NUMBER VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Sequence Number Validation',
    CASE
        WHEN COUNT_IF(sequence_no < 0) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(sequence_no < 0)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 10: DISTANCE DATA AVAILABILITY
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Distance Data Availability',
    CASE
        WHEN COUNT(*) > 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM DISTANCE_DATA;


-- ============================================================
-- TEST 11: DISTANCE DATA ROW COUNT
-- Expected: 500
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Distance Data Row Count',
    CASE
        WHEN COUNT(*) = 500 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM DISTANCE_DATA;


-- ============================================================
-- TEST 12: DISTANCE VALUE VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Distance Value Validation',
    CASE
        WHEN COUNT_IF(distance_to_nearest_store_m < 0) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(distance_to_nearest_store_m < 0)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM DISTANCE_DATA;


-- ============================================================
-- TEST 13: NEAREST STORE VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Nearest Store Validation',
    CASE
        WHEN COUNT_IF(nearest_store_id IS NULL) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(nearest_store_id IS NULL)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM DISTANCE_DATA;


-- ============================================================
-- TEST 14: FOOTFALL SUMMARY AVAILABILITY
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Footfall Summary Availability',
    CASE
        WHEN COUNT(*) > 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM FOOTFALL_SUMMARY;


-- ============================================================
-- TEST 15: FOOTFALL SUMMARY ROW COUNT
-- Expected: 3
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Footfall Summary Row Count',
    CASE
        WHEN COUNT(*) = 3 THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT(*)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM FOOTFALL_SUMMARY;


-- ============================================================
-- TEST 16: FOOTFALL VALUE VALIDATION
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'Footfall Value Validation',
    CASE
        WHEN COUNT_IF(total_visits < 0) = 0
         AND COUNT_IF(total_dwell_minutes < 0) = 0
         AND COUNT_IF(unique_visitors < 0) = 0
         AND COUNT_IF(avg_dwell_minutes < 0) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    (
        COUNT_IF(total_visits < 0)
        + COUNT_IF(total_dwell_minutes < 0)
        + COUNT_IF(unique_visitors < 0)
        + COUNT_IF(avg_dwell_minutes < 0)
    )::VARCHAR,
    CURRENT_TIMESTAMP()
FROM FOOTFALL_SUMMARY;


-- ============================================================
-- TEST 17: GPS DATA FRESHNESS
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'GPS Data Freshness',
    CASE
        WHEN MAX(timestamp) IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    MAX(timestamp)::VARCHAR,
    CURRENT_TIMESTAMP()
FROM GPS_DATA;


-- ============================================================
-- TEST 18: PIPELINE OVERALL STATUS
-- ============================================================

INSERT INTO PIPELINE_TEST_RESULTS
SELECT
    'OVERALL PIPELINE STATUS',
    CASE
        WHEN COUNT_IF(TEST_RESULT = 'FAIL') = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    COUNT_IF(TEST_RESULT = 'FAIL')::VARCHAR || ' tests failed',
    CURRENT_TIMESTAMP()
FROM PIPELINE_TEST_RESULTS;


-- ============================================================
-- FINAL RESULTS
-- ============================================================

SELECT
    TEST_NAME,
    TEST_RESULT,
    TEST_VALUE,
    TEST_TIMESTAMP
FROM PIPELINE_TEST_RESULTS
ORDER BY TEST_TIMESTAMP;