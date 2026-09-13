# ================================================
# Air Pollution AQI Prediction Model
# Tool: Apache Spark MLlib
# Algorithm: Linear Regression
# Input: cleaned data from HDFS
# Output: model results and predictions
# ================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg
from pyspark.sql.functions import round as spark_round
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline
import numpy

# ------------------------------------------------
# Start Spark Session
# ------------------------------------------------
spark = SparkSession.builder \
    .appName("AQIPredictionModel") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=== AQI Prediction Model Started ===")

# ------------------------------------------------
# Load Cleaned Data from HDFS
# ------------------------------------------------
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

# ------------------------------------------------
# Feature Engineering
# ------------------------------------------------
print("\n=== Preparing Features ===")

# Convert City to numeric using StringIndexer
city_indexer = StringIndexer(
    inputCol="City",
    outputCol="City_Index"
)

# Convert Month to numeric
df = df.withColumn("Month", col("Month").cast("integer"))

# Select features for prediction
feature_cols = [
    "City_Index", "Month",
    "PM25", "PM10", "NO", "NO2",
    "NOx", "NH3", "CO", "SO2", "O3"
]

# Combine all features into one vector
assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features",
    handleInvalid="skip"
)

# ------------------------------------------------
# Build Pipeline
# ------------------------------------------------
lr = LinearRegression(
    featuresCol="features",
    labelCol="AQI",
    maxIter=100,
    regParam=0.1,
    elasticNetParam=0.0
)

pipeline = Pipeline(stages=[
    city_indexer,
    assembler,
    lr
])

# ------------------------------------------------
# Split Data: 80% Training, 20% Testing
# ------------------------------------------------
print("\n=== Splitting Data 80/20 ===")
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
print(f"Training records: {train_data.count()}")
print(f"Testing records:  {test_data.count()}")

# ------------------------------------------------
# Train the Model
# ------------------------------------------------
print("\n=== Training Linear Regression Model ===")
model = pipeline.fit(train_data)
print("Model training complete!")

# ------------------------------------------------
# Make Predictions
# ------------------------------------------------
print("\n=== Making Predictions ===")
predictions = model.transform(test_data)

# Show sample predictions
print("\nSample Predictions vs Actual AQI:")
predictions.select(
    "City", "Month", "PM25",
    "AQI", "prediction"
).show(20)

# ------------------------------------------------
# Evaluate Model
# ------------------------------------------------
print("\n=== Model Evaluation ===")

# R² Score
evaluator_r2 = RegressionEvaluator(
    labelCol="AQI",
    predictionCol="prediction",
    metricName="r2"
)
r2 = evaluator_r2.evaluate(predictions)
print(f"R² Score:  {round(r2, 4)}")

# RMSE
evaluator_rmse = RegressionEvaluator(
    labelCol="AQI",
    predictionCol="prediction",
    metricName="rmse"
)
rmse = evaluator_rmse.evaluate(predictions)
print(f"RMSE:      {round(rmse, 4)}")

# MAE
evaluator_mae = RegressionEvaluator(
    labelCol="AQI",
    predictionCol="prediction",
    metricName="mae"
)
mae = evaluator_mae.evaluate(predictions)
print(f"MAE:       {round(mae, 4)}")

# ------------------------------------------------
# Save Predictions to HDFS
# ------------------------------------------------
print("\n=== Saving Predictions ===")
predictions.select(
    "City", "Date", "Month",
    "PM25", "PM10", "AQI",
    "prediction"
).write.csv(
    "hdfs://localhost:9000/air_pollution/output/predictions",
    header=True,
    mode="overwrite"
)
print("Predictions saved to HDFS!")

# ------------------------------------------------
# Save Model Metrics
# ------------------------------------------------
metrics_data = [(
    "Linear Regression",
    round(r2, 4),
    round(rmse, 4),
    round(mae, 4)
)]

metrics_df = spark.createDataFrame(
    metrics_data,
    ["Model", "R2_Score", "RMSE", "MAE"]
)
metrics_df.show()
metrics_df.write.csv(
    "hdfs://localhost:9000/air_pollution/output/model_metrics",
    header=True,
    mode="overwrite"
)

print("\n=== Prediction Model Complete! ===")
spark.stop()