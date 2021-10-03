"""
Author: Shubham Bhatnagar
Date Created: 21/09/2021 20:17
Last Updated: 27/09/2021 16:03

Unit test file for StockOutlierCheck class. Test cases are defined below:
1) Testing StockOutlierCheck class instantiation
    a) Can create an instance of StockOutlierCheck
    b) Incorrect file path when creating class instance raises FileNotFoundError
2) Testing set_df_index_to_date function 
    a) If date column or price column doesn't exist in source data, raise Exception
    b) Raises Error if data format is wrong
    c) Updates data type to datetime correctly and sets "Date" to index
3) Testing take_first_difference
    a) Rolling first difference correctly calculated in test df. First
        value is NaN
    b) Percentage change correctly calculated
4) Testing identify_outliers
    a) Check if, for provided dataframe, values correctly identified as outlier.
    b) Check if re-running with difference sensitivity value works correctly
5) Testing clean_stock_data
    a) Check if, once outliers identified, they are removed from df correctly
6)  Testing write_cleaned_data_to_csv
    a) Check if output path is correctly identified (assuming df.to_csv works 
        out of the box).

Note: No plotting functions are tested as can assume matplotlib.pyplot works
as intended and this is a side feature for this use case. Future work may involve
more in depth test cases e.g. may want to test input x, y iterables have
compatible sizes and so on.

"""
# Imports
import numpy as np
import pytest
import os
import sys
import pandas as pd
from unittest.mock import Mock, patch
from _pytest.fixtures import SubRequest

# Ensure the root of the project is in the repo
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from src.stock_outlier import StockOutlierChecker

# Creating Test Class
class TestStockOutlierCheck:

    # Class variable to store the data file location
    data_file = os.path.join(sys.path[0], "..", "data", "Outliers.csv")

    @pytest.fixture(autouse=True)
    @patch("src.stock_outlier.pd.read_csv")
    def create_stock_object(self, mock_read_csv: Mock, request: SubRequest) -> None:
        """Base fixture that creates a StockOutlierChecker instance and stores
        it to self.stock. The read_csv is patched and the return df is mocked
        to a simple 4 row df that is tested across other methods

        Args:
            mock_read_csv (Mock): Mocked read_csv that returns sample df
            request (SubRequest): Pytest request when fixture is called enabling
                certain test methods to interact with this fixture
        """

        # Creating sample dataframe when read_csv is called
        mock_read_csv.return_value = pd.DataFrame(
            {
                "Date": [
                    pd.to_datetime("2021-09-19", format="%Y-%m-%d"),
                    pd.to_datetime("2021-09-20", format="%Y-%m-%d"),
                    pd.to_datetime("2021-09-21", format="%Y-%m-%d"),
                    pd.to_datetime("2021-09-22", format="%Y-%m-%d"),
                ],
                "Price": [0, 600, 800, 1200],
            }
        )

        # Using registered custom markers to differentiate when to use/not use
        # this fixture
        if "noautofixt" in request.keywords:
            return
        else:
            self.stock = StockOutlierChecker(TestStockOutlierCheck.data_file)


    # Test marked to not use base fixture
    @pytest.mark.noautofixt
    def test_incorrect_file_path(self) -> None:
        """Testing if class instantiation with incorrect file path raises
        FileNotFoundError
        """

        # Checking if FileNotFoundError raised for non-existent file path
        with pytest.raises(FileNotFoundError):
            incorr_file = os.path.join(sys.path[0], "Incorrect.csv")
            StockOutlierChecker(incorr_file)


    # Test marked to not use base fixture, read_csv mocked to return specific
    # dataframe and parameterized to cover all 3 cases of missing columns
    @pytest.mark.noautofixt
    @patch("src.stock_outlier.pd.read_csv")
    @pytest.mark.parametrize(
        "c1, c2, v",
        [
            ("Time", "Close", "Date, Price"),
            ("Price", "Time", "Date"),
            ("Close", "Date", "Price"),
        ],
        ids=["Both Missing", "Date Missing", "Price Missing"],
    )
    def test_price_and_date_in_df(
        self, mock_read_csv: Mock, c1: str, c2: str, v: str
    ) -> None:
        """Testing if the Date and/or Price columns are missing in the source
        data, the correct exceptions are raised

        Args:
            mock_read_csv (Mock): Mock read csv to return specified dataframe
            c1 (str): Parametrized column 1 name
            c2 (str): Parametrized column 2 name
            v (str): Expected exception output based on test case
        """

        # Parametrized sample df representing erroneous source data
        df = pd.DataFrame(
            {
                c1: [
                    pd.to_datetime("2021-09-20", format="%Y-%m-%d"),
                    pd.to_datetime("2021-09-21", format="%Y-%m-%d"),
                    pd.to_datetime("2021-09-22", format="%Y-%m-%d"),
                ],
                c2: [600, 800, 1200],
            }
        )

        # when read_csv is called, erroneous dataframe created
        mock_read_csv.return_value = df

        # Check if correct error is raised
        with pytest.raises(Exception) as e:
            StockOutlierChecker(TestStockOutlierCheck.data_file)

        # Assert error message correctly identifies which columns are missing
        assert str(e.value) == f"Column(s) '{v}' is/are missing from df"


    def test_incorrect_date_format_when_setting_index(self) -> None:
        """Test if the date data is in the wrong format, value error is raised"""

        df = pd.DataFrame(
            {
                "Date": ["2021-09-20", " 2021-09-21", "2021-09-22"],
                "Price": [600, 800, 1200],
            }
        )

        self.stock.df = df
        with pytest.raises(Exception) as e:
            self.stock.set_df_index_to_date()

        assert str(e.value) == "Date format does not match '%d/%m/%Y'"


    def test_date_column_when_setting_index(self) -> None:
        """Check if date datatype correctly updated and if index is set to Date
        column
        """

        # Create source data to have str 'Date' column that is not the index
        df = pd.DataFrame(
            {
                "Date": ["20/09/2021", "21/09/2021", "22/09/2021"],
                "Price": [600, 800, 1200],
            }
        )

        # Overwriting the base fixture return df with function specific df
        self.stock.df = df

        # Calling set df index function on data
        self.stock.set_df_index_to_date()

        # Asserting the index column is now the 'Date' column
        assert self.stock.df.index.name == "Date"
        # Asserting the data type of the index is datetime
        assert self.stock.df.index.dtype == "datetime64[ns]"

    
    def test_first_difference_values(self) -> None:
        """Test if the first difference function correctly calculates the
        first difference for the given dataframe
        """

        # Calculating the first difference
        self.stock.take_first_difference()

        # parsing the first difference series into a list
        first_diff_result = [x for x in self.stock.df["Rolling Difference"].values]

        # Asserting the first value is null
        assert pd.isnull(first_diff_result[0])
        # Asserting the rest matches the expected values
        assert sorted(first_diff_result[1:]) == [200, 400, 600]

    
    def test_first_difference_pcnt_change(self) -> None:
        """Test if the first difference function also calculates the percent
        change correctly.
        """

        # Calling the first difference function
        self.stock.take_first_difference()

        # Parsing the percentage change values into list
        pcnt_change_result = [x for x in self.stock.df["Pcnt Change"].values]

        # Asserting the first value is null
        assert pd.isnull(pcnt_change_result[0])

        # Asserting the second value is inf as divide by 0
        assert pcnt_change_result[1] == np.inf

        # Asserting the percentage differences are approx equal ( i.e. floating
        # point errors are ignored)
        assert sorted(pcnt_change_result[2:]) == [
            pytest.approx(1 / 3),
            pytest.approx(0.5),
        ]

    
    def test_identify_outliers_correctly_finds_outliers(self) -> None:
        """Testing if outlier identification function correctly picks outliers
        from given dataframe
        """

        # Creating known outlier based df
        df = pd.DataFrame(
            {
                "Date": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "Pcnt Change": [
                    np.nan,
                    -0.011,
                    0.01,
                    0.4,
                    -0.37,
                    -0.02,
                    -1.1,
                    1.0,
                    0.01,
                    -0.01,
                ],
                "Price": [100, 99, 101, 140, 102, 101, 2, 102, 102.3, 101.9],
            }
        )

        # Overriting base fixture df with local df
        self.stock.df = df

        # Calling the identify outlier function
        self.stock.identify_outliers()

        # Checking the outliers correctly identified by looking at their dates
        assert sorted(self.stock.outliers["Date"].values) == [4, 7]

    
    def test_identify_outliers_rerun_works_correctly(self) -> None:
        """Test if re-running the outlier identification function correctly
        resets the outlier df and identifies new outliers (e.g. if
        acceptable_pcnt_change value changed)
        """

        # Creating known outlier based df
        df = pd.DataFrame(
            {
                "Date": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "Pcnt Change": [
                    np.nan,
                    -0.011,
                    0.01,
                    0.4,
                    -0.37,
                    -0.02,
                    -1.1,
                    1.0,
                    0.01,
                    -0.01,
                ],
                "Price": [100, 99, 101, 140, 102, 101, 2, 102, 102.3, 101.9],
            }
        )

        # Overriting base fixture df with local df
        self.stock.df = df

        # Calling function with default value
        self.stock.identify_outliers()
        # Calling function again with acceptable pcnt change of 1000%
        self.stock.identify_outliers(acceptable_pcnt_change=10)

        # Assert outliers df correctly identified after re-run
        assert sorted(self.stock.outliers["Date"].values) == []

    
    def test_clean_stock_data(self) -> None:
        """Testing if for a given outliers df and stock price df, the outliers
        are removed from the stock price df.
        """

        # Creating stock price df with outliers
        self.stock.df = pd.DataFrame(
            {
                "Date": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 200],
                "Price": [100, 99, 101, 140, 102, 101, 2, 102, 102.3, 101.9, 0, 10000],
            }
        )

        # Creating outliers df
        self.stock.outliers = pd.DataFrame(
            {
                "Date": [4, 7, 100, 200],
                "Price": [140, 2, 0, 10000],
            }
        )

        # Calling the clean function
        self.stock.clean_stock_data()

        # Asserting the stock price df has all outliers removed
        assert set(~self.stock.df.index.isin(self.stock.outliers.index)) == {True}

    
    @patch("src.stock_outlier.pd.DataFrame.to_csv")
    def test_write_cleaned_data_to_csv_basename_check(self, mock_to_csv: Mock) -> None:
        """Mocking the df.to_csv function such that no output file is created.
        Instead can assume this pandas method works as intended. Instead test
        if the basename for the new output file is correctly identified.

        Args:
            mock_to_csv (Mock): Mock object to replace df.to_csv method
        """
        # Simply return saved when the df.to_csv() method called as no need to
        # test actual to_csv method, can assume it works
        mock_to_csv.return_value = "Saved"

        # Calling the write to csv function
        self.stock.write_cleaned_data_to_csv()

        # Asserting the output path is correctly identified i.e. 'Cleaned_'
        # prepended to filename
        correct_out_path = os.path.join(
            sys.path[0], "..", "data", "Cleaned_Outliers.csv"
        )
        mock_to_csv.assert_called_once_with(correct_out_path)
