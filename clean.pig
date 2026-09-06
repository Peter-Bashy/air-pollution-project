-- ================================================
-- Air Pollution Data Cleaning Script
-- Tool: Apache Pig
-- Input: /air_pollution/raw/city_day.csv
-- Output: /air_pollution/cleaned
-- ================================================

-- Step 1: Load raw data from HDFS
pollution = LOAD '/air_pollution/raw/city_day.csv'
USING PigStorage(',')
AS (
    City:chararray,
    Date:chararray,
    PM25:double,
    PM10:double,
    NO:double,
    NO2:double,
    NOx:double,
    NH3:double,
    CO:double,
    SO2:double,
    O3:double,
    Benzene:double,
    Toluene:double,
    Xylene:double,
    AQI:double,
    AQI_Bucket:chararray
);

-- Step 2: Remove header row
data_no_header = FILTER pollution BY City != 'City';

-- Step 3: Remove rows where City is null or empty
valid_city = FILTER data_no_header BY
             City IS NOT NULL AND
             City != '';

-- Step 4: Remove rows where Date is null or empty
valid_date = FILTER valid_city BY
             Date IS NOT NULL AND
             Date != '';

-- Step 5: Remove rows where AQI is null
valid_aqi = FILTER valid_date BY
            AQI IS NOT NULL;

-- Step 6: Remove rows where AQI is negative
-- Zero AQI is kept and will be handled in Spark
valid_values = FILTER valid_aqi BY AQI >= 0;

-- Step 7: Remove rows where AQI_Bucket is null or empty
valid_bucket = FILTER valid_values BY
               AQI_Bucket IS NOT NULL AND
               AQI_Bucket != '';

-- Step 8: Trim spaces and replace null pollutants with 0
-- Note: NO, NO2, NOx etc can genuinely be zero
-- PM25 and PM10 zeros will be handled in Spark
trimmed = FOREACH valid_bucket GENERATE
    TRIM(City) AS City,
    TRIM(Date) AS Date,
    (PM25 IS NULL ? 0.0 : PM25) AS PM25,
    (PM10 IS NULL ? 0.0 : PM10) AS PM10,
    (NO IS NULL ? 0.0 : NO) AS NO,
    (NO2 IS NULL ? 0.0 : NO2) AS NO2,
    (NOx IS NULL ? 0.0 : NOx) AS NOx,
    (NH3 IS NULL ? 0.0 : NH3) AS NH3,
    (CO IS NULL ? 0.0 : CO) AS CO,
    (SO2 IS NULL ? 0.0 : SO2) AS SO2,
    (O3 IS NULL ? 0.0 : O3) AS O3,
    (Benzene IS NULL ? 0.0 : Benzene) AS Benzene,
    (Toluene IS NULL ? 0.0 : Toluene) AS Toluene,
    (Xylene IS NULL ? 0.0 : Xylene) AS Xylene,
    AQI AS AQI,
    TRIM(AQI_Bucket) AS AQI_Bucket;

-- Step 9: Extract Year and Month from Date
transformed = FOREACH trimmed GENERATE
    City,
    Date,
    SUBSTRING(Date, 0, 4) AS Year,
    SUBSTRING(Date, 5, 7) AS Month,
    PM25, PM10,
    NO, NO2, NOx,
    NH3, CO, SO2, O3,
    Benzene, Toluene, Xylene,
    AQI, AQI_Bucket;

-- Step 10: Remove duplicate rows
distinct_data = DISTINCT transformed;

-- Step 11: Store final cleaned data back to HDFS
STORE distinct_data
INTO '/air_pollution/cleaned'
USING PigStorage(',');