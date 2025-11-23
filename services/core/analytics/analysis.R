#!/usr/bin/env Rscript
# FarmTech Analytics - R Analysis Script
# Performs statistical analysis on sensor data

library(jsonlite)

# Get arguments
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("No input file provided")
}

# Read JSON data
data_file <- args[1]
tryCatch({
  data <- fromJSON(readLines(data_file))
}, error = function(e) {
  stop(paste("Failed to read JSON file:", e$message))
})

# Convert to numeric vector
values <- as.numeric(unlist(data))

# Check for valid data
if (length(values) == 0) {
  stop("No numeric values found in input data")
}

# Remove NaN and Inf values
values <- values[!is.na(values) & !is.infinite(values)]

if (length(values) == 0) {
  stop("All values are NaN or Inf")
}

# Calculate statistics
result <- list(
  mean_value = mean(values, na.rm = TRUE),
  median_value = median(values, na.rm = TRUE),
  sd_value = sd(values, na.rm = TRUE),
  min_value = min(values, na.rm = TRUE),
  max_value = max(values, na.rm = TRUE),
  count = length(values),
  timestamp = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ")
)

# Output as JSON
cat(toJSON(result, pretty = TRUE))
