# ================================================
# Air Pollution R Visualization
# Tool: R + ggplot2
# Input: CSV files from Spark analytics
# Output: PNG chart files
# ================================================

library(ggplot2)
library(dplyr)
library(readr)

# Set working directory
setwd("/workspaces/air-pollution-project")

# Create output folder for charts
dir.create("charts", showWarnings = FALSE)

# ------------------------------------------------
# Graph 1: Average AQI by City (Horizontal Bar)
# ------------------------------------------------
city_aqi <- read_csv("city_aqi.csv", show_col_types = FALSE)
colnames(city_aqi) <- c("City", "Avg_AQI")
city_aqi$Avg_AQI <- as.numeric(city_aqi$Avg_AQI)
city_aqi <- city_aqi[!is.na(city_aqi$Avg_AQI), ]

ggplot(city_aqi, aes(x = reorder(City, Avg_AQI), y = Avg_AQI, fill = Avg_AQI)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_gradient(low = "yellow", high = "red") +
  labs(
    title = "Average AQI by City",
    subtitle = "Higher AQI = More Polluted",
    x = "City",
    y = "Average AQI",
    fill = "AQI"
  ) +
  theme_minimal()

ggsave("charts/01_avg_aqi_by_city.png", width = 10, height = 8)
cat("Graph 1 saved!\n")

# ------------------------------------------------
# Graph 2: Top 10 Most Polluted Cities (Vertical Bar)
# ------------------------------------------------
top10 <- read_csv("top10_cities.csv", show_col_types = FALSE)
colnames(top10) <- c("City", "Avg_AQI")
top10$Avg_AQI <- as.numeric(top10$Avg_AQI)
top10 <- top10[!is.na(top10$Avg_AQI), ]

ggplot(top10, aes(x = reorder(City, -Avg_AQI), y = Avg_AQI, fill = City)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = Avg_AQI), vjust = -0.5, size = 3.5) +
  labs(
    title = "Top 10 Most Polluted Cities",
    subtitle = "Based on Average AQI 2015-2020",
    x = "City",
    y = "Average AQI"
  ) +
  theme_minimal() +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("charts/02_top10_polluted_cities.png", width = 10, height = 6)
cat("Graph 2 saved!\n")

# ------------------------------------------------
# Graph 3: Year-wise AQI Trend (Line Chart)
# ------------------------------------------------
year_aqi <- read_csv("year_aqi.csv", show_col_types = FALSE)
colnames(year_aqi) <- c("Year", "Avg_AQI")
year_aqi$Avg_AQI <- as.numeric(year_aqi$Avg_AQI)
year_aqi <- year_aqi[!is.na(year_aqi$Avg_AQI), ]

ggplot(year_aqi, aes(x = Year, y = Avg_AQI, group = 1)) +
  geom_line(color = "steelblue", linewidth = 1.5) +
  geom_point(color = "red", size = 4) +
  geom_text(aes(label = Avg_AQI), vjust = -1, size = 3.5) +
  labs(
    title = "Year-wise AQI Trend (2015-2020)",
    subtitle = "AQI decreasing over years — COVID lockdown visible in 2020",
    x = "Year",
    y = "Average AQI"
  ) +
  theme_minimal()

ggsave("charts/03_yearwise_aqi_trend.png", width = 10, height = 6)
cat("Graph 3 saved!\n")

# ------------------------------------------------
# Graph 4: Monthly AQI Trend (Line Chart)
# ------------------------------------------------
month_aqi <- read_csv("month_aqi.csv", show_col_types = FALSE)
colnames(month_aqi) <- c("Month", "Avg_AQI")
month_aqi$Avg_AQI <- as.numeric(month_aqi$Avg_AQI)
month_aqi <- month_aqi[!is.na(month_aqi$Avg_AQI) & !is.na(month_aqi$Month), ]

# Fix: use numeric months 1-12
month_aqi$Month <- as.integer(month_aqi$Month)
month_aqi <- month_aqi[month_aqi$Month >= 1 & month_aqi$Month <= 12, ]
month_aqi$Month_Name <- factor(month_aqi$Month,
  levels = 1:12,
  labels = c("Jan","Feb","Mar","Apr","May","Jun",
             "Jul","Aug","Sep","Oct","Nov","Dec"))

ggplot(month_aqi, aes(x = Month_Name, y = Avg_AQI, group = 1)) +
  geom_line(color = "darkgreen", linewidth = 1.5) +
  geom_point(color = "orange", size = 4) +
  geom_text(aes(label = Avg_AQI), vjust = -1, size = 3.5) +
  labs(
    title = "Monthly AQI Trend (Seasonal Patterns)",
    subtitle = "Monsoon season (Jun-Sep) shows lowest pollution",
    x = "Month",
    y = "Average AQI"
  ) +
  theme_minimal()

ggsave("charts/04_monthly_aqi_trend.png", width = 10, height = 6)
cat("Graph 4 saved!\n")

# ------------------------------------------------
# Graph 5: AQI Category Distribution (Pie Chart)
# with AQI Scale inside
# ------------------------------------------------
aqi_cat <- read_csv("aqi_category.csv", show_col_types = FALSE)
colnames(aqi_cat) <- c("Category", "Count")
aqi_cat$Count <- as.numeric(aqi_cat$Count)
aqi_cat <- aqi_cat[!is.na(aqi_cat$Count), ]

# Add AQI range to category labels
aqi_cat$Label <- case_when(
  aqi_cat$Category == "Good"         ~ "Good\n(0-50)",
  aqi_cat$Category == "Satisfactory" ~ "Satisfactory\n(51-100)",
  aqi_cat$Category == "Moderate"     ~ "Moderate\n(101-200)",
  aqi_cat$Category == "Poor"         ~ "Poor\n(201-300)",
  aqi_cat$Category == "Very Poor"    ~ "Very Poor\n(301-400)",
  aqi_cat$Category == "Severe"       ~ "Severe\n(401-500)",
  TRUE ~ aqi_cat$Category
)

# Define colors matching AQI scale
aqi_colors <- c(
  "Good\n(0-50)"           = "#00B050",
  "Satisfactory\n(51-100)" = "#92D050",
  "Moderate\n(101-200)"    = "#FFFF00",
  "Poor\n(201-300)"        = "#FF7C00",
  "Very Poor\n(301-400)"   = "#FF0000",
  "Severe\n(401-500)"      = "#7030A0"
)

ggplot(aqi_cat, aes(x = "", y = Count, fill = Label)) +
  geom_bar(stat = "identity", width = 1, color = "white") +
  coord_polar("y", start = 0) +
  scale_fill_manual(values = aqi_colors) +
  geom_text(aes(label = paste0(Count, " days")),
            position = position_stack(vjust = 0.5), size = 3.5) +
  labs(
    title = "AQI Category Distribution",
    subtitle = "Based on Indian AQI Scale",
    fill = "AQI Category"
  ) +
  theme_void() +
  theme(legend.position = "right",
        legend.text = element_text(size = 10),
        plot.title = element_text(hjust = 0.5, size = 14),
        plot.subtitle = element_text(hjust = 0.5, size = 10))

ggsave("charts/05_aqi_category_distribution.png", width = 10, height = 8)
cat("Graph 5 saved!\n")

# ------------------------------------------------
# Graph 6: Severe Pollution Days by City (Horizontal Bar)
# ------------------------------------------------
severe <- read_csv("severe_days.csv", show_col_types = FALSE)
colnames(severe) <- c("City", "Severe_Days")
severe$Severe_Days <- as.numeric(severe$Severe_Days)
severe <- severe[!is.na(severe$Severe_Days), ]

ggplot(severe, aes(x = reorder(City, Severe_Days), y = Severe_Days, fill = Severe_Days)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_gradient(low = "orange", high = "darkred") +
  geom_text(aes(label = Severe_Days), hjust = -0.2, size = 3.5) +
  labs(
    title = "Severe + Very Poor Pollution Days by City",
    subtitle = "Number of days with AQI > 300",
    x = "City",
    y = "Number of Days",
    fill = "Days"
  ) +
  theme_minimal()

ggsave("charts/06_severe_pollution_days.png", width = 10, height = 8)
cat("Graph 6 saved!\n")

# ------------------------------------------------
# Graph 7: PM2.5 vs AQI (Scatter Plot)
# Fix: Filter AQI <= 500 and PM25 <= 500
# ------------------------------------------------
pm25_aqi <- read_csv("pm25_aqi.csv", show_col_types = FALSE)
colnames(pm25_aqi) <- c("City", "Date", "PM25", "AQI")
pm25_aqi$PM25 <- as.numeric(pm25_aqi$PM25)
pm25_aqi$AQI <- as.numeric(pm25_aqi$AQI)

# Filter valid range
pm25_aqi <- pm25_aqi[!is.na(pm25_aqi$PM25) &
                     !is.na(pm25_aqi$AQI) &
                     pm25_aqi$AQI >= 1 &
                     pm25_aqi$AQI <= 500 &
                     pm25_aqi$PM25 > 0 &
                     pm25_aqi$PM25 <= 500, ]

ggplot(pm25_aqi, aes(x = PM25, y = AQI, color = City)) +
  geom_point(alpha = 0.5, size = 1.5) +
  geom_smooth(method = "lm", color = "black", se = FALSE) +
  labs(
    title = "PM2.5 vs AQI Scatter Plot",
    subtitle = "Strong positive correlation between PM2.5 and AQI",
    x = "PM2.5 Concentration",
    y = "AQI (0-500)",
    color = "City"
  ) +
  theme_minimal() +
  theme(legend.position = "right")

ggsave("charts/07_pm25_vs_aqi.png", width = 12, height = 8)
cat("Graph 7 saved!\n")

# ------------------------------------------------
# Graph 8: Pollutant Correlation Heatmap
# ------------------------------------------------
corr_data <- read_csv("correlation.csv", show_col_types = FALSE)
colnames(corr_data) <- c("Pollutant", "Correlation")
corr_data$Correlation <- as.numeric(corr_data$Correlation)
corr_data <- corr_data[!is.na(corr_data$Correlation), ]

ggplot(corr_data, aes(x = "AQI", y = reorder(Pollutant, Correlation), fill = Correlation)) +
  geom_tile(color = "white") +
  geom_text(aes(label = Correlation), size = 4) +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0) +
  labs(
    title = "Pollutant Correlation with AQI",
    subtitle = "Red = strong correlation, Blue = negative correlation",
    x = "",
    y = "Pollutant",
    fill = "Correlation"
  ) +
  theme_minimal()

ggsave("charts/08_pollutant_correlation_heatmap.png", width = 8, height = 8)
cat("Graph 8 saved!\n")

# ------------------------------------------------
# Graph 9: City vs Month AQI Heatmap
# Fix: use numeric months, handle missing data
# ------------------------------------------------
city_month <- read_csv("city_month_aqi.csv", show_col_types = FALSE)
colnames(city_month) <- c("City", "Month", "Avg_AQI")
city_month$Avg_AQI <- as.numeric(city_month$Avg_AQI)
city_month$Month <- as.integer(city_month$Month)

# Remove NA and invalid months
city_month <- city_month[!is.na(city_month$Avg_AQI) &
                         !is.na(city_month$Month) &
                         city_month$Month >= 1 &
                         city_month$Month <= 12, ]

# Convert month numbers to names
city_month$Month_Name <- factor(city_month$Month,
  levels = 1:12,
  labels = c("Jan","Feb","Mar","Apr","May","Jun",
             "Jul","Aug","Sep","Oct","Nov","Dec"))

ggplot(city_month, aes(x = Month_Name, y = City, fill = Avg_AQI)) +
  geom_tile(color = "white") +
  scale_fill_gradient(low = "green", high = "red", na.value = "grey90") +
  geom_text(aes(label = Avg_AQI), size = 2.5) +
  labs(
    title = "City vs Month AQI Heatmap",
    subtitle = "Grey = data not available for that month",
    x = "Month",
    y = "City",
    fill = "Avg AQI"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("charts/09_city_month_heatmap.png", width = 14, height = 10)
cat("Graph 9 saved!\n")

# ------------------------------------------------
# Graph 10: AQI Spread by City (Boxplot)
# Fix: Cap values at 500
# ------------------------------------------------
city_spread <- read_csv("city_spread.csv", show_col_types = FALSE)
colnames(city_spread) <- c("City", "Min_AQI", "Max_AQI", "Avg_AQI", "Q1", "Median", "Q3")
city_spread$Min_AQI <- as.numeric(city_spread$Min_AQI)
city_spread$Max_AQI <- as.numeric(city_spread$Max_AQI)
city_spread$Avg_AQI <- as.numeric(city_spread$Avg_AQI)
city_spread$Q1 <- as.numeric(city_spread$Q1)
city_spread$Median <- as.numeric(city_spread$Median)
city_spread$Q3 <- as.numeric(city_spread$Q3)
city_spread <- city_spread[!is.na(city_spread$Avg_AQI), ]

# Cap all values at 500 (standard AQI scale)
city_spread$Max_AQI <- ifelse(city_spread$Max_AQI > 500, 500, city_spread$Max_AQI)
city_spread$Q3 <- ifelse(city_spread$Q3 > 500, 500, city_spread$Q3)
city_spread$Median <- ifelse(city_spread$Median > 500, 500, city_spread$Median)

ggplot(city_spread, aes(x = reorder(City, Avg_AQI))) +
  geom_boxplot(
    aes(ymin = Min_AQI, lower = Q1, middle = Median, upper = Q3, ymax = Max_AQI),
    stat = "identity",
    fill = "steelblue",
    alpha = 0.7
  ) +
  coord_flip() +
  scale_y_continuous(limits = c(0, 500)) +
  labs(
    title = "AQI Spread by City (Boxplot)",
    subtitle = "Shows min, Q1, median, Q3, max AQI per city (capped at 500)",
    x = "City",
    y = "AQI (0-500)"
  ) +
  theme_minimal()

ggsave("charts/10_aqi_spread_boxplot.png", width = 10, height = 8)
cat("Graph 10 saved!\n")

cat("\n=== All Visualizations Complete! ===\n")
cat("Charts saved in /workspaces/air-pollution-project/charts/\n")