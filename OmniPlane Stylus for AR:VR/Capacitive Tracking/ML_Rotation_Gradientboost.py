import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import numpy as np
import mysql.connector
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

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
query = f"SELECT {input_columns}, {output_columns} FROM Electrodes1"

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

# Initialize the XGBClassifier with 100 trees
model = XGBClassifier(n_estimators=100, random_state=42)

# Train the model
model.fit(train_inputs, train_outputs)

# Get the probability predictions for each class on the test set
predictions_proba = model.predict_proba(test_inputs)

# Create a DataFrame for the predictions probabilities
predictions_proba_df = pd.DataFrame(predictions_proba, columns=[f"output{i}" for i in range(1, 82)])

# Save the predictions probabilities to a CSV file
predictions_proba_df.to_csv('predictions_proba.csv', index=False)

# Get the predictions (0 or 1) by thresholding the probabilities (you can adjust the threshold)
predictions = (predictions_proba > 0.5).astype(int)

# Count the number of trees voting for each output
trees_voting_count = predictions.sum(axis=1)

# Add the voting count to the predictions DataFrame
predictions_with_vote_count = pd.concat([predictions_proba_df, pd.DataFrame({'trees_voting_count': trees_voting_count})], axis=1)

# Save the updated predictions DataFrame to a CSV file
predictions_with_vote_count.to_csv('predictions_with_vote_count.csv', index=False)

# Calculate the accuracy for each output
output_accuracies = [accuracy_score(test_outputs.iloc[:, i], predictions[:, i]) for i in range(81)]

# Reshape the accuracies into a 9x9 array
output_accuracies_matrix = np.array(output_accuracies).reshape(9, 9)

# Create a Seaborn heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(output_accuracies_matrix, annot=True, fmt=".2%", cmap="Blues", cbar_kws={'label': 'Accuracy'})
plt.title("Accuracy for Each Output")
plt.xlabel("Output Index")
plt.ylabel("Output Index")
plt.show()
