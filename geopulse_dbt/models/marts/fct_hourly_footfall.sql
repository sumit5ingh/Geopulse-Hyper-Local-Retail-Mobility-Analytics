{{ config(
    materialized='table'
) }}

SELECT
    EVENT_HOUR,
    COUNT(*) AS TOTAL_PINGS,
    COUNT(DISTINCT DEVICE_ID) AS UNIQUE_DEVICES
FROM {{ ref('stg_gps_pings') }}
GROUP BY EVENT_HOUR
ORDER BY EVENT_HOUR