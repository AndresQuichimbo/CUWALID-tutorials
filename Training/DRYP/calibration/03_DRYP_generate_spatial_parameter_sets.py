import numpy as np
import pandas as pd

# generate a dataframe with n rows and m columns, where each column contains random numbers
# between min and max. The columns should be named "col1", "col2", ..., "colm".
# min and max values are provided as arrays of length m, where min[i] and
# max[i] correspond to the minimum and maximum values for column i.

n = 100
m = 23

# The best and worst values are used to calculate the variance, which is then used to set the min and max values for each column. The first 7 columns have a wider range of values, while the remaining columns are set to 1.0.
best_value = 0.359163
worst_value = 0.392913
variance = np.abs(best_value - worst_value)

# Set the min and max values for each column based on the best value and variance. The first 7 columns have a wider range, while the remaining columns are set to 1.0.
min_values = np.full(m, best_value - variance)
max_values = np.full(m, best_value + variance)

# Set the min and max values for the first 7 columns to be wider than the remaining columns, which are set to 1.0.
min_values[7:] = best_value
max_values[7:] = best_value

# Generate random data for each column based on the specified min and max values. The first 7 columns will have a wider range of values, while the remaining columns will be set to 1.0.
data = np.random.rand(n, m) * (max_values - min_values) + min_values

# Scale the first column by a factor of 1.0 to adjust the range of values. This is done to ensure that the first column has a similar range of values as the other columns, which are set to 1.0.
factor = 1.0
#data[:, 0] = data[:, 0] * factor

# Create a DataFrame from the generated data, with column names "col1", "col2", ..., "colm". The DataFrame will have n rows and m columns, where each column contains random numbers between the specified min and max values.
df = pd.DataFrame(data, columns=[f"col{i+1}" for i in range(m)])

# Save the DataFrame to a CSV file named "random_data.csv". The CSV file will contain the generated random data, with column names as headers.
path_spatial_paramters = "/user/work/km19051/HAD_basin/calibration/HAD_spatial_parameter_range_file_JU.csv"
df.to_csv(path_spatial_paramters, index=False)
