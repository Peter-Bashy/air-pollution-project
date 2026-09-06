# ================================================
# Air Pollution Spark Analytics
# ================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, when, min, max, percentile_approx
from pyspark.sql.functions import round as spark_round
from builtins import round as py_round

# Start Spark Session
spark = SparkSession.builder \
    .appName("AirPollutionAnalytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=== Spark Session Started ===")

# Load Cleaned Data from HDFS
df = spark.read.csv(
    "hdfs://localhost:9000/air_pollution/cleaned/part-r-00000",
    header=False,
    inferSchema=True
)

# Rename columns
df = df.toDF(
    "City", "Date", "Year", "Month",
    "PM25", "PM10", "NO", "NO2", "NOx",
    "NH3", "CO", "SO2", "O3",
    "Benzene", "Toluene", "Xylene",
    "AQI", "AQI_Bucket"
)

print(f"Total records loaded: {df.count()}")

# ------------------------------------------------
# Fill Zero Values with City Average
# ------------------------------------------------
print("\n=== Filling Zero Values with City Average ===")

city_avg = df.groupBy("City").agg(
    avg(when(col("AQI") > 0, col("AQI"))).alias("avg_AQI"),
    avg(when(col("PM25") > 0, col("PM25"))).alias("avg_PM25"),
    avg(when(col("PM10") > 0, col("PM10"))).alias("avg_PM10")
)

df = df.join(city_avg, on="City", how="left")

df = df.withColumn("AQI",
    when(col("AQI") == 0, spark_round(col("avg_AQI"), 2))
    .otherwise(col("AQI"))
)
df = df.withColumn("PM25",
    when(col("PM25") == 0, spark_round(col("avg_PM25"), 2))
    .otherwise(col("PM25"))
)
df = df.withColumn("PM10",
    when(col("PM10") == 0, spark_round(col("avg_PM10"), 2))
    .otherwise(col("PM10"))
)

df = df.drop("avg_AQI", "avg_PM25", "avg_PM10")

print(f"Total records after filling zeros: {df.count()}")

# ------------------------------------------------
# Analysis 1: Average AQI by City
# ------------------------------------------------
print("\n=== Analysis 1: Average AQI by City ===")
city_aqi = df.groupBy("City") \
    .agg(spark_round(avg("AQI"), 2).alias("Avg_AQI")) \
    .orderBy("Avg_AQI", ascending=False)
city_aqi.show()
city_aqi.write.csv(
    "hdfs://localhost:9000/air_pollution/output/city_aqi",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 2: Top 10 Most Polluted Cities
# ------------------------------------------------
print("\n=== Analysis 2: Top 10 Most Polluted Cities ===")
top10 = city_aqi.limit(10)
top10.show()
top10.write.csv(
    "hdfs://localhost:9000/air_pollution/output/top10_cities",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 3: Year-wise AQI Trend
# ------------------------------------------------
print("\n=== Analysis 3: Year-wise AQI Trend ===")
year_aqi = df.groupBy("Year") \
    .agg(spark_round(avg("AQI"), 2).alias("Avg_AQI")) \
    .orderBy("Year")
year_aqi.show()
year_aqi.write.csv(
    "hdfs://localhost:9000/air_pollution/output/year_aqi",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 4: Monthly AQI Trend
# ------------------------------------------------
print("\n=== Analysis 4: Monthly AQI Trend ===")
month_aqi = df.groupBy("Month") \
    .agg(spark_round(avg("AQI"), 2).alias("Avg_AQI")) \
    .orderBy("Month")
month_aqi.show()
month_aqi.write.csv(
    "hdfs://localhost:9000/air_pollution/output/month_aqi",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 5: AQI Category Distribution
# ------------------------------------------------
print("\n=== Analysis 5: AQI Category Distribution ===")
aqi_category = df.groupBy("AQI_Bucket") \
    .agg(count("AQI_Bucket").alias("Count")) \
    .orderBy("Count", ascending=False)
aqi_category.show()
aqi_category.write.csv(
    "hdfs://localhost:9000/air_pollution/output/aqi_category",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 6: Severe Pollution Days by City
# ------------------------------------------------
print("\n=== Analysis 6: Severe Pollution Days by City ===")
severe_days = df.filter(
    (col("AQI_Bucket") == "Severe") |
    (col("AQI_Bucket") == "Very Poor")
) \
    .groupBy("City") \
    .agg(count("City").alias("Severe_Days")) \
    .orderBy("Severe_Days", ascending=False)
severe_days.show()
severe_days.write.csv(
    "hdfs://localhost:9000/air_pollution/output/severe_days",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 7: PM2.5 vs AQI
# ------------------------------------------------
print("\n=== Analysis 7: PM2.5 vs AQI ===")
pm25_aqi = df.select("City", "Date", "PM25", "AQI") \
    .filter(col("PM25") > 0)
pm25_aqi.show(10)
pm25_aqi.write.csv(
    "hdfs://localhost:9000/air_pollution/output/pm25_aqi",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 8: Pollutant Correlation with AQI
# ------------------------------------------------
print("\n=== Analysis 8: Pollutant Correlation with AQI ===")
pollutants = ["PM25", "PM10", "NO", "NO2",
              "NOx", "NH3", "CO", "SO2",
              "O3", "Benzene", "Toluene", "Xylene"]

correlation_data = []
for p in pollutants:
    correlation = df.stat.corr(p, "AQI")
    corr_value = py_round(float(correlation), 4)
    correlation_data.append((p, corr_value))
    print(f"{p} vs AQI correlation: {corr_value}")

corr_df = spark.createDataFrame(
    correlation_data,
    ["Pollutant", "Correlation"]
).orderBy("Correlation", ascending=False)
corr_df.show()
corr_df.write.csv(
    "hdfs://localhost:9000/air_pollution/output/correlation",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 9: City vs Month AQI (for Heatmap)
# ------------------------------------------------
print("\n=== Analysis 9: City vs Month AQI ===")
city_month_aqi = df.groupBy("City", "Month") \
    .agg(spark_round(avg("AQI"), 2).alias("Avg_AQI")) \
    .orderBy("City", "Month")
city_month_aqi.show()
city_month_aqi.write.csv(
    "hdfs://localhost:9000/air_pollution/output/city_month_aqi",
    header=True, mode="overwrite"
)

# ------------------------------------------------
# Analysis 10: AQI Spread by City (for Boxplot)
# ------------------------------------------------
print("\n=== Analysis 10: AQI Spread by City ===")
city_spread = df.groupBy("City") \
    .agg(
        spark_round(min("AQI"), 2).alias("Min_AQI"),
        spark_round(max("AQI"), 2).alias("Max_AQI"),
        spark_round(avg("AQI"), 2).alias("Avg_AQI"),
        spark_round(percentile_approx("AQI", 0.25), 2).alias("Q1"),
        spark_round(percentile_approx("AQI", 0.5), 2).alias("Median"),
        spark_round(percentile_approx("AQI", 0.75), 2).alias("Q3")
    ) \
    .orderBy("Avg_AQI", ascending=False)
city_spread.show()
city_spread.write.csv(
    "hdfs://localhost:9000/air_pollution/output/city_spread",
    header=True, mode="overwrite"
)

print("\n=== All Analytics Complete! ===")
spark.stop()