"""
Author: Shubham Bhatnagar
Date Created: 21/09/2021 20:17
Last Updated: 27/09/2021 12:58

Module defining class and methods required for stock outlier checking.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt


class StockOutlierChecker:
    """A class to find and remove outliers in a stock price dataset based on
    price percentage change and acceptable tolerance (5% by default).
    ...

    Attributes
    ----------
    csv_path : str
        Filepath of CSV where stock price data is stored

    outliers: pandas.DataFrame
        DataFrame containing all outliers found


    Methods
    -------
    read_csv()
        Use pandas read_csv method to read csv_path attribute to df

    set_df_index_to_date()
        For time series data, set date col to df index and type to datetime

    plot_price_chart(show=False)
        Plot Date against Price, show if flag enabled.

    take_first_difference()
        Calculate first difference & percent change of price to prev value.

    identify_outliers(acceptable_pcnt_change=0.05)
        Identify if value in time series is an outlier based on % change.
        acceptable_pcnt_change variable controls sensitivity.

    plot_outliers()
        Plot original price df and overlay outliers in red

    clean_stock_data()
        Remove outliers from original df.

    write_cleaned_data_to_csv()
        Write df attribute to csv in same location & prepend 'Cleaned ' to name.
    """

    def __init__(self, csv_path: str) -> None:
        """Constructs all necessary attributes for class instance.

        Args:
            csv_path (str): Absolute path where CSV file is located
        """

        # Assign and create instance variables
        self.csv_path = csv_path
        self.outliers = None

        # Read csv to df for given csv_path
        self.read_csv()


    def read_csv(self) -> None:
        """Reads csv_path to dataframe and stores to self.df attribute using
        pandas read_csv method. Checks if date and price columns exist, else
        raises exception.

        Raises
            Exception: If price and/or Date columns are missing from data.
        """

        # Read csv path and store dataframe as instance attribute self.df
        self.df = pd.read_csv(self.csv_path)

        # If date and/or price not in data columns
        if "Date" not in self.df.columns or "Price" not in self.df.columns:
            # Calculate which column is missing
            missing = {"Date", "Price"} - set(self.df.columns)
            # Format missing column to single string
            missing = ", ".join(sorted(list(missing)))
            # Raise exception, printing what is missing
            raise Exception(f"Column(s) '{missing}' is/are missing from df")


    def set_df_index_to_date(self) -> None:
        """Sets date column to type datetime64 and assigns it df index.

        Raises
            ValueError: If Date format does not match expected '%d/%m/%Y'
        """

        # If date column type is not datetime64[ns] then update to it
        if self.df["Date"].dtype != "datetime64[ns]":
            # Set data type to datetime
            try:
                self.df["Date"] = pd.to_datetime(self.df["Date"], format="%d/%m/%Y")
            # if value error raised, date format incorrect
            except ValueError:
                raise Exception("Date format does not match '%d/%m/%Y'")

        # Set the "Date" column as the index
        self.df.set_index("Date", inplace=True)


    def plot_price_chart(
        self, title: str = "Stock Price Data", show: bool = False
    ) -> None:
        """Plot a chart for the df "Date" and "Price" columns. The plot is not
        shown by default as all charts are shown at the end of the outlier
        process but this can be enabled.

        Args:
            title (str, optional): Chart title. Defaults to "Stock Price Data".
            show (bool, optional): Flag to indicate if plot should be shown.
                Defaults to False.
        """

        # Create a new matplotlib figure
        plt.figure()
        # Plot figure and format it
        plt.plot(self.df.index, self.df["Price"])
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(title)

        # Only show if show flag is set
        if show:
            plt.show()


    def take_first_difference(self) -> None:
        """Take first difference of price using a rolling window of 2."""

        # Calculate rolling difference from each time step and it's previous
        self.df["Rolling Difference"] = (
            self.df["Price"].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0])
        )

        # Compute a percent change by dividing by old price
        self.df["Pcnt Change"] = self.df["Rolling Difference"] / self.df["Price"].shift(
            1
        )


    def identify_outliers(self, acceptable_pcnt_change: float = 0.05) -> None:
        """Identify outliers in data by checking where price % change exceeds
        acceptable level. The acceptable_pcnt_change input can be used to change
        tolerance of method to volatility. The identified outliers are added
        to the instance outlier dataframe.

        Args:
            acceptable_pcnt_change (float, optional): [description]. Defaults to 0.05.

        To Do:
            Handle case where two anomalous data points follow each other
        """

        # Reset outlier df ensure user can alter acceptable_pcnt_change and
        # re-run the checks
        self.outliers = None

        # Identify where the % change exceeds to acceptable level
        temp_outliers = self.df[abs(self.df["Pcnt Change"]) > acceptable_pcnt_change]

        # For each anomaly, there is a large change before and after it. In
        # these cases, identify them and flag the second large change as
        # a complementary/return to 'normal' change
        complementary_change = self.df[
            abs(self.df["Pcnt Change"].shift(1)) > acceptable_pcnt_change
        ]

        # Remove these complementary change data points from outlier list
        self.outliers = pd.concat(
            [
                self.outliers,
                temp_outliers[~temp_outliers.index.isin(complementary_change.index)],
            ]
        )

        # Print the outliers df to stdout
        print(f"Found {len(self.outliers)} outliers in data:\n")
        print(self.outliers[["Price"]])


    def plot_outliers(self, show: bool = False) -> None:
        """Plot outliers (in red) ontop of the stock price data (in blue).

        Args
            show (bool, optional): Flag to indicate if plot should be shown.
                    Defaults to False.
        """

        # Plot the stock price data and outliers on top of each other
        plt.figure()
        plt.plot(self.df.index, self.df["Price"])
        plt.scatter(self.outliers.index, self.outliers["Price"], c="r")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("Stock Price Data with Outliers Overlayed")
        if show:
            plt.show()


    def clean_stock_data(self) -> None:
        """Once outliers have been identified remove them from the source df."""

        # Remove where df index value is in outliers df index
        self.df = self.df[~self.df.index.isin(self.outliers.index)]


    def write_cleaned_data_to_csv(self) -> None:
        """Write cleaned df back to csv in same location with 'Cleaned'
        prepended.
        """

        # Get the tail of the path i.e. file name
        old_basename = os.path.basename(self.csv_path)
        # Prepend 'Cleaned' to file name
        basename = "Cleaned_" + old_basename

        # Construct new file path by replace filename with new value
        self.out_path = self.csv_path.replace(old_basename, basename)

        # Write data to csv
        self.df[["Price"]].to_csv(self.out_path)
