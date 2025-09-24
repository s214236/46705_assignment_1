"placeholder for various utils functions"

import json
import csv
import pandas as pd
import os

# example function to load data from a specified directory
def load_dataset(question_name):
    base_path = os.path.join("data", question_name)
    result = {}
 
    for file_path in os.listdir(base_path):
        full_path = os.path.join(base_path, file_path)
        if file_path.endswith('.json'):
            with open(full_path, 'r') as f:
                result[file_path] = json.load(f)
        print(f"Done reading {file_path}")
 
    return result

# example function to save model results in a specified directory
def save_model_results():
    """Placeholder for save_model_results function."""
    pass

# example function to plot data from a specified directory
def plot_data():
    """Placeholder for plot_data function."""
    pass


# Testing
if __name__ == "__main__":
    result = load_dataset("question_1a")
    print(result)