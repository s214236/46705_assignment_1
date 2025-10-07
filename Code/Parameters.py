import os
import json
import numpy as np


class Parameters:
    def __init__(self, dataset_folder: str):
        # Load dataset
        self.data = self.load_datasets(dataset_folder)

        # Initialize flags for the existence of optional components
        self.storage_exists = False
        self.min_combined_load_exists = False
        self.desired_load_exists = False

        # Extract parameter selections from the data
        pv_data = self.data["appliance_params.json"]["DER"][0]
        load_data = self.data["appliance_params.json"]["load"][0]
        bus_data = self.data["bus_params.json"][0]
        production_data = self.data["DER_production.json"][0]
        usage_data = self.data["usage_preferences.json"][0]

        # Time horizon
        self.T = len(bus_data["energy_price_DKK_per_kWh"])  # Number of hours

        # Load and PV parameters
        self.pv_max = pv_data["max_power_kW"] * np.array(
            production_data["hourly_profile_ratio"]
        )  # Max PV power per hour
        self.load_max = load_data["max_load_kWh_per_hour"]  # Max load per hour
        self.import_max = bus_data["max_import_kW"]  # Max import power
        self.export_max = bus_data["max_export_kW"]  # Max export power

        # Price parameters
        self.electricity_price = np.array(bus_data["energy_price_DKK_per_kWh"])
        self.import_price = (
            self.electricity_price + bus_data["import_tariff_DKK/kWh"]
        )  # Cost for import
        self.export_price = (
            self.electricity_price - bus_data["export_tariff_DKK/kWh"]
        )  # Revenue for export

        # Desired load structure parameters
        load_preferences = usage_data["load_preferences"][0]
        if load_preferences["min_total_energy_per_day_hour_equivalent"] is not None:
            self.min_combined_load_exists = True
            self.min_combined_load = (
                load_preferences["min_total_energy_per_day_hour_equivalent"]
                * self.load_max
            )  # Minimum combined load per day

        if load_preferences["hourly_profile_ratio"] is not None:
            self.desired_load_exists = True
            self.desired_load = (
                np.array(load_preferences["hourly_profile_ratio"]) * self.load_max
            )  # Desired load profile

        # Storage parameters are defined if they exist in the data
        if self.data["appliance_params.json"].keys().__contains__("storage"):
            if self.data["appliance_params.json"]["storage"] is not None:
                self.storage_exists = True
                storage_data = self.data["appliance_params.json"]["storage"][0]
                self.storage_capacity = storage_data["storage_capacity_kWh"]
                self.charging_efficiency = storage_data["charging_efficiency"]
                self.discharging_efficiency = storage_data["discharging_efficiency"]
                self.charging_capacity = (
                    storage_data["max_charging_power_ratio"] * self.storage_capacity
                )
                self.discharging_capacity = (
                    storage_data["max_discharging_power_ratio"] * self.storage_capacity
                )
                self.initial_soc = (
                    usage_data["storage_preferences"][0]["initial_soc_ratio"]
                    * self.storage_capacity
                )
                self.final_soc = (
                    usage_data["storage_preferences"][0]["final_soc_ratio"]
                    * self.storage_capacity
                )

    def load_datasets(self, dataset_folder: str) -> dict:
        """Load and combine all datasets for a given question.

        Args:
            dataset_folder (str): question folder name.

        Returns:
            dict: Combined datasets from the specified question folder.
        """
        base_path = os.path.join("data", dataset_folder)
        data = {}

        for file_path in os.listdir(base_path):
            full_path = os.path.join(base_path, file_path)
            if file_path.endswith(".json"):
                with open(full_path, "r") as f:
                    data[file_path] = json.load(f)

        return data


# Testing
if __name__ == "__main__":
    parameters = Parameters("question_1a")
    print("Parameters loaded successfully.")
