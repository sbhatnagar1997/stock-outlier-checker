# **Stock Price Data Outlier Identifier**

The following python module takes in a 'Outliers.csv' file with 2 columns: 'Date' and 'Price', identifies any outliers in the time series data, removes them and outputs the cleaned data to a CSV file called 'Cleaned_Outliers.csv' in the same location. It also ensures no forward bias in this process by using a rolling window and only comparing each new price point to its history.

Finally, the user can define an `acceptable_pcnt_change` value (default = 0.05 i.e. 5%) to control the sensitivity of the outlier identifier. A high value should be used for volatile stocks and a low value for stable stocks. This can be tuned with historical data if needed.

### **How To Use**

1. Download and unzip the zip file
2. Create a virtual environment using virtualenv in the unzipped folder
  a. `virtualenv venv`
  b. Note: if the above doesn't work, run `pip install virtualenv`
3. Activate the virtual environment (assuming windows)
  a.`venv\scripts\activate`
4. Install the requirements file
  a. `pip install -r requirements.txt`
5. Run the `find_outliers.py` file in the scripts folder
  a. `cd scripts`
  b. `python find_outliers.py`
6. A cleaned version of the data is created in the data folder called `'Cleaned_Outliers.csv'`

### Known Issues
##### No matching pandas distribution found for 1.X.X
This is caused by inconsistent python versions. To fix please follow:
1) Comment out `pandas` line in requirements by putting a `#` in front of the relevant line
    a. pandas\==1.3.3 -> #pandas==1.3.3
2) Re-run `pip install -r requirements.txt`
3) Run `pip install pandas`

For any further issues, please contact `12shubham1@gmail.com`

### **Testing and Documentation**

##### Testing
A set of unit tests have been written for the source code using the `pytest` module along with `mocking/patching` from unittests to isolate each method being tested. 

To run the tests:
1) `cd tests` (assuming you are in the root folder of this project)
2) `pytest . -v` (the 'v' option prints a verbose output)

##### Coverage Report
A coverage report for the tests has also been run. Navigate and open `tests\htmlcov\index.html` for more details. As documented in the test files, the matplotlib plotting functions were not included in unit tests and hence the coverage is not 100%.

To run the coverage report for yourself (view the output in the same way as above via index.html):
1) `cd tests` (assuming you are in the root folder of this project)
2) `coverage run --omit '*/venv/*' -m pytest`
3) `coverage html`

##### Documentation
The code has also been documented across the user script, source code and unit tests to clarify the purpose, structure and thought process behind development.

### **Future Work**

An experimental ARIMA model was also built in this project. This model aimed to use a rolling window to ensure no forward bias. The model would be used to predict the stock price at each new time point. Once all predictions were made, an absolute error was calculated for each prediction to actual value. If this error was above a specified threshold, then it was classified to be an outlier. However, the model (p,d,q) was picked randomly and this is an area I would need guidance on in the future.

In addition, if working in a software development environment, I would have also created a git repository to track all changes/features being added. This is another area of improvement in the future.