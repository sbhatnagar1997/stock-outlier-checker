"""
Author: Shubham Bhatnagar
Date Created: 21/09/2021 20:17
Last Updated: 27/09/2021 12:56

Using time series data provided, identify and remove outliers. 

Rules:
1) Ignore/don't use forward bias
2) Output cleaned dataset to new CSV file.

Outlier identification process:
1) Explore data visually

2) Identify if time series is stationary 
- i.e. look for trend, cyclicality/seasonality

3) Make data stationary if non-stationary
- Take first difference and check if stationary

4) Identify outliers based on tolerance for price change percentage to previous
point

5) Write data back to CSV
"""

# =============================================================================
# Imports
# =============================================================================
import os
import sys

# Ensure the root of the project is in the system path
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from src.stock_outlier import StockOutlierChecker

# Only allow the script to be executed directly, not imported
if __name__ == "__main__":
    pass
else:
    sys.exit()

# =============================================================================
# Read data from CSV
# =============================================================================
# CSV file path
csv_file = os.path.join(sys.path[0], "..", "data", "Outliers.csv")

# Create class instance and read csv automatically
stock = StockOutlierChecker(csv_file)

# Set date to index
stock.set_df_index_to_date()

# Initial data investigation
stock.plot_price_chart(title="Initial Stock Price Data")

# =============================================================================
# Identify if time series is stationary by visually looking for trend/seasonality
# =============================================================================

# Data is volatile and has upwards trends

# =============================================================================
# Making time series data stationary
# =============================================================================
# As data is not stationary, take first difference to remove trend.
# Use a rolling window ensures no forward bias is introduced
stock.take_first_difference()

# =============================================================================
# Identify outliers
# =============================================================================
# Identify outliers
stock.identify_outliers()
# Plot outliers on top of price data
stock.plot_outliers()

# Clean data df to remove outliers
stock.clean_stock_data()

# =============================================================================
# Write back to CSV
# =============================================================================
stock.write_cleaned_data_to_csv()

# =============================================================================
# Plotting Cleaned Data
# =============================================================================
stock.plot_price_chart(title="Cleaned Stock Price Data", show=True)
