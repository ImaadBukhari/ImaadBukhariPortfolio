import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import mysql.connector
import os

# Connect to MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='Stylus_Data'
)

# Generate column names for inputs (input1, input2, ..., input108)
input_columns_str = ", ".join(f"input{i}" for i in range(1, 109))
input_columns_list = [f"input{i}" for i in range(1, 109)]

# Generate column names for outputs (output1, output2, ..., output81)
output_columns_str = ", ".join(f"output{i}" for i in range(1, 82))
output_columns_list = [f"output{i}" for i in range(1, 82)]

# Construct the SQL query
query = f"SELECT {input_columns_str}, {output_columns_str} FROM Electrodes1"

# Fetch data from MySQL into a Pandas DataFrame
df = pd.read_sql_query(query, connection)

# Close the database connection
connection.close()

index_dict = [41,32,33,42,51,50,49,40,31,22,23,24,25,34,43,52,61,60,59,58,57,48,39,30,21,12,13,14,15,16,17,26,35,44,53,62,71,70,69,68,67,66,65,56,47,38,29,20,11,2,3,4,5,6,7,8,9,18,27,36,45,54,63,72,81,80,79,78,77,76,75,74,73,64,55,46,37,28,19,10,1]


# Create a dictionary to store the trained models
models = {}

# Use all previous outputs as inputs
input_features = input_columns_list 

# Set random seed for reproducibility
np.random.seed(42)

# Shuffle the DataFrame rows randomly
df = df.sample(frac=1).reset_index(drop=True)

# Split data into training and test sets (80-20 split)
train_size = int(0.8 * len(df))
train_df = df[:train_size]
test_df = df[train_size:]
predictions_equiv = pd.DataFrame()
ind = 0 

# Check if the file from the previous step exists
if os.path.exists("previous_predictions.csv"):
    # Load previous predictions into a DataFrame
    previous_predictions_df = pd.read_csv("previous_predictions.csv")
    existing_columns = []
    for i in range(len(previous_predictions_df.columns)):
        # Append the corresponding output column name to existing_columns
        existing_columns.append(output_columns_list[index_dict[i]])
        ind = i
    predictions_equiv = train_df[existing_columns].copy()
        
else:
    # Create an empty DataFrame if the file doesn't exist
    previous_predictions_df = pd.DataFrame()

if not predictions_equiv.empty:
    X_train = train_df[input_features].fillna(0) + predictions_equiv.iloc[:,:ind].fillna(0)
else:
    X_train = train_df[input_features].copy()
X_test = test_df[input_features] + previous_predictions_df

if not previous_predictions_df.empty:
    X_test = test_df[input_features].fillna(0) + previous_predictions_df.fillna(0)
else:
    X_test = test_df[input_features].copy()



# Open CSV file in 'append' mode to store predictions
with open("current_predictions.csv", "a") as file:
    # Loop through models
    for i in range(40, 81):
        print(f"Start training model {i+1}")

        # Select the relevant data for the current output
        current_output_col = output_columns_list[index_dict[i]]
        y_train = train_df[current_output_col]  # Current output in training set
        y_test = test_df[current_output_col]    # Current output in test set

    
        # Train a random forest model
        try:
            model = RandomForestClassifier()
            model.fit(X_train, y_train)

            # Save the trained model
            models[f"model_output{index_dict[i]}"] = model

            # Predict the current output on the test set
            predictions = model.predict(X_test)

            # Count correct predictions and update the CSV file
            correct_predictions = np.sum(predictions == y_test)
            file.write(f"{correct_predictions},")

            # Update the test_df with predictions
            X_test[f"output_col{index_dict[i]}"] = predictions
            X_train[f"output_col{index_dict[i]}"] = train_df[f"output{index_dict[i]}"]

            print(f"Training and predictions complete for model {i+1}")

        except Exception as e:
            print(f"Error in training model {i+1}: {str(e)}")

        

        print(f"End of model {i+1}")
        

print("Correct predictions appended to 'current_predictions.csv'.")

# Concatenate current predictions with previous predictions
all_predictions_df = pd.concat([previous_predictions_df, test_df.filter(like='output_pred')], axis=1)

# Save all predictions to a CSV file for future use
all_predictions_df.to_csv("previous_predictions.csv", index=False)

# Save the trained models
for name, model in models.items():
    dump(model, f"{name}.joblib")
    print(f"Model {name} saved.")

print("Training and saving complete.")

