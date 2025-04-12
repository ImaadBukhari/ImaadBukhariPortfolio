import pandas as pd
from sklearn.model_selection import train_test_split
import mysql.connector
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from joblib import dump, load

clf = load('trained_model.joblib') 

# Connect to MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='Stylus_Data'
)

# Generate column names for inputs (input1, input2, ..., input108)
input_columns = ", ".join(f"input{i}" for i in range(1, 109))

# Generate column names for outputs (output1, output2, ..., output81)
output_columns = ", ".join(f"output{i}" for i in range(1, 82))

# Construct the SQL query
query = f"SELECT {input_columns}, {output_columns} FROM Electrodes"

# Fetch data from MySQL into a Pandas DataFrame
df = pd.read_sql_query(query, connection)

# Close the database connection
connection.close()

# Separate input and output columns
inputs = df.iloc[:, :108]
outputs = df.iloc[:, 108:]

# Split the data into training and test sets (80-20 split)
train_inputs, test_inputs, train_outputs, test_outputs = train_test_split(
    inputs, outputs, test_size=0.2, random_state=42)

print('x')
predictions = clf.predict(test_inputs)
print('y')

# Initialize a list to store the count of correct predictions for each output
correct_predictions_count = [0] * 81

# Iterate through predictions and test_outputs
for prediction, true_output in zip(predictions, test_outputs.values):
    for output_index, predicted_class in enumerate(prediction):
        if predicted_class == true_output[output_index]:
            correct_predictions_count[output_index] += 1

# Reshape the correct predictions count list into a 9x9 array
correct_predictions_matrix = np.array(correct_predictions_count).reshape((9, 9))

# Create a subplot for the heatmap
fig, ax = plt.subplots(figsize=(9, 9))

# Plot Heatmap for Correct Predictions
sns.heatmap(correct_predictions_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=range(1, 10), yticklabels=range(1, 10), ax=ax)
ax.set_title('Correct Predictions Count (Output vs. Prediction)')

# Show the plot
plt.show()



