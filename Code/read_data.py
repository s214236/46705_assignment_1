import os
import json


def load_datasets(question_name: str):
    base_path = os.path.join("data", question_name)
    result = {}

    for file_path in os.listdir(base_path):
        full_path = os.path.join(base_path, file_path)
        if file_path.endswith(".json"):
            with open(full_path, "r") as f:
                result[file_path] = json.load(f)
        print(f"Done reading {file_path}")

    return result


# Testing
if __name__ == "__main__":
    result = load_datasets("question_1a")
    print(result)
