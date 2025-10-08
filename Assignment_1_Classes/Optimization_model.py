import numpy as np
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
from Assignment_1_Classes.Parameters import Parameters


class Optimization_model:
    def __init__(self):
        self.model = None
        self.status = "Empty model"

    def load_data(self, dataset_folder: str) -> None:
        self.parameters = Parameters(dataset_folder)
        self.parameters.diff_penalty = (
            GRB.INFINITY
        )  # Penalty for deviation from desired load
        self.status = "Data loaded"

    def create_model(self) -> None:
        self.model = gp.Model("Energy System Optimization")
        self.status = "Model created"
        self._add_variables()
        self._add_objective()
        self._add_constraints()

    def optimize(self) -> None:
        self.model.optimize()
        if self.model.status == GRB.OPTIMAL:
            self.status = "Model optimized"
        else:
            self.status = "Model infeasible or unbounded"

    def get_results(self) -> dict:
        if self.model.status != GRB.OPTIMAL:
            raise ValueError("No optimal solution available.")

        results = {}
        results["objective_value"] = self.model.objVal
        results["load"] = [
            self.model.getVarByName(f"load_{t}").x for t in range(self.parameters.T)
        ]
        results["pv_prod"] = [
            self.model.getVarByName(f"gen_{t}").x for t in range(self.parameters.T)
        ]
        results["pv_curtailment"] = [
            self.parameters.pv_max[t] - results["pv_prod"][t]
            for t in range(self.parameters.T)
        ]
        results["import_grid"] = [
            self.model.getVarByName(f"import_{t}").x for t in range(self.parameters.T)
        ]
        results["export_grid"] = [
            self.model.getVarByName(f"export_{t}").x for t in range(self.parameters.T)
        ]
        results["charge"] = (
            [self.model.getVarByName(f"charge_{t}").x for t in range(self.parameters.T)]
            if self.parameters.storage_exists
            else [0] * self.parameters.T
        )
        results["discharge"] = (
            [
                self.model.getVarByName(f"discharge_{t}").x
                for t in range(self.parameters.T)
            ]
            if self.parameters.storage_exists
            else [0] * self.parameters.T
        )
        results["soc"] = (
            [self.model.getVarByName(f"SOC_{t}").x for t in range(self.parameters.T)]
            if self.parameters.storage_exists
            else [0] * self.parameters.T
        )
        results["battery_size"] = (
            self.parameters.storage_capacity
            * (
                self.model.getVarByName("battery_scaling").x
                if self.parameters.battery_size_variable
                else 1
            )
            if self.parameters.storage_exists
            else 0
        )

        return results

    def plot_results(self) -> None:
        # Extract results
        results = self.get_results()

        # Plotting
        plt.figure()
        plt.plot(results["load"], label="Load (kW)", color="blue")
        plt.plot(results["pv_prod"], label="PV Production (kW)", color="orange")
        plt.plot(results["pv_curtailment"], label="PV Curtailment (kW)", color="red")
        plt.plot(
            results["import_grid"],
            label="Import from Grid (kW)",
            color="green",
            linestyle="--",
        )
        plt.plot(
            results["export_grid"],
            label="Export to Grid (kW)",
            color="red",
            linestyle="--",
        )
        plt.plot(
            self.parameters.electricity_price,
            label="Electricity Price (DKK/kWh)",
            color="purple",
            linestyle=":",
        )
        if self.parameters.desired_load_exists:
            plt.plot(
                self.parameters.desired_load,
                label="Desired Load (kW)",
                color="brown",
                linestyle="--",
            )
        if self.parameters.storage_exists:
            plt.plot(
                results["charge"],
                label="Storage Charge (kW)",
                color="cyan",
                linestyle=":",
            )
            plt.plot(
                results["discharge"],
                label="Storage Discharge (kW)",
                color="magenta",
                linestyle=":",
            )
            plt.plot(
                results["soc"], label="Storage SOC (kWh)", color="gray", linestyle="--"
            )
        plt.legend()
        plt.xlabel("Time (hours)")
        plt.ylabel("Power (kW) / Energy (kWh) / Price (DKK/kWh)")
        plt.title("Energy System Optimization Results")
        plt.grid()
        plt.show()

    def set_battery_size_as_variable(self) -> None:
        if not self.parameters.storage_exists:
            raise ValueError(
                "No storage data available to set battery size as variable."
            )
        self.parameters.battery_size_variable = True
        self.parameters.battery_cost = GRB.INFINITY

    def _add_variables(self) -> None:
        # Initialize variable dictionaries
        self.var = {}
        self.var["load"] = {}
        self.var["gen"] = {}
        self.var["import"] = {}
        self.var["export"] = {}
        self.var["pos_diff_load"] = {}
        self.var["neg_diff_load"] = {}
        self.var["discharge"] = {}
        self.var["charge"] = {}
        self.var["SOC"] = {}

        # Add variables with no timestep dependency
        # Adding storage capacity as a variable if specified
        if self.parameters.battery_size_variable:
            self.var["battery_scaling"] = self.model.addVar(
                name="battery_scaling", lb=0, ub=GRB.INFINITY
            )

        # Add variables for each time step
        for t in range(self.parameters.T):
            # Basic variables
            self.var["load"][t] = self.model.addVar(
                name=f"load_{t}", lb=0, ub=self.parameters.load_max
            )
            self.var["gen"][t] = self.model.addVar(
                name=f"gen_{t}", lb=0, ub=self.parameters.pv_max[t]
            )
            self.var["import"][t] = self.model.addVar(
                name=f"import_{t}", lb=0, ub=self.parameters.import_max
            )
            self.var["export"][t] = self.model.addVar(
                name=f"export_{t}", lb=0, ub=self.parameters.export_max
            )

            # Desired load variables if relevant
            if self.parameters.desired_load_exists:
                self.var["pos_diff_load"][t] = self.model.addVar(
                    name=f"pos_diff_load_{t}", lb=0
                )
                self.var["neg_diff_load"][t] = self.model.addVar(
                    name=f"neg_diff_load_{t}", lb=0
                )

            # Storage variables if relevant
            if self.parameters.storage_exists:
                self.var["discharge"][t] = self.model.addVar(
                    name=f"discharge_{t}",
                    lb=0,
                )
                self.var["charge"][t] = self.model.addVar(
                    name=f"charge_{t}",
                    lb=0,
                )
                self.var["SOC"][t] = self.model.addVar(
                    name=f"SOC_{t}",
                    lb=0,
                )

        # Update model to integrate new variables
        self.model.update()
        self.status += "\nVariables added"

    def _add_objective(self) -> None:
        # Setting the objective function
        self.obj = self.model.setObjective(
            gp.quicksum(
                self.parameters.import_price[t] * self.var["import"][t]
                - self.parameters.export_price[t] * self.var["export"][t]
                + (
                    self.parameters.diff_penalty
                    * (self.var["pos_diff_load"][t] + self.var["neg_diff_load"][t])
                    if self.parameters.desired_load_exists
                    else 0
                )
                for t in range(self.parameters.T)
            )
            + (
                self.parameters.battery_cost * self.var["battery_scaling"]
                if self.parameters.battery_size_variable
                else 0
            ),
            GRB.MINIMIZE,
        )

        # Update model to integrate new objective
        self.model.update()
        self.status += "\nObjective added"

    def _add_constraints(self) -> None:
        # Initialize constraint dictionary
        self.constr = {}

        # Energy balance constraint
        for t in range(self.parameters.T):
            self.constr[f"energy_balance_{t}"] = self.model.addLConstr(
                self.var["load"][t]
                + self.var["export"][t]
                + (self.var["charge"][t] if self.parameters.storage_exists else 0),
                GRB.EQUAL,
                self.var["gen"][t]
                + self.var["import"][t]
                + (self.var["discharge"][t] if self.parameters.storage_exists else 0),
                name=f"energy_balance_{t}",
            )

        # Minimum combined load constraint if relevant
        if self.parameters.min_combined_load_exists:
            self.constr["minimum_combined_load"] = self.model.addLConstr(
                gp.quicksum(self.var["load"][t] for t in range(self.parameters.T)),
                GRB.GREATER_EQUAL,
                self.parameters.min_combined_load,
                name="minimum_combined_load",
            )

        # Desired load profile constraints if relevant
        if self.parameters.desired_load_exists:
            for t in range(self.parameters.T):
                self.constr[f"pos_diff_load_{t}"] = self.model.addLConstr(
                    self.var["pos_diff_load"][t],
                    GRB.GREATER_EQUAL,
                    self.var["load"][t] - self.parameters.desired_load[t],
                    name=f"pos_diff_load_{t}",
                )
                self.constr[f"neg_diff_load_{t}"] = self.model.addLConstr(
                    self.var["neg_diff_load"][t],
                    GRB.GREATER_EQUAL,
                    self.parameters.desired_load[t] - self.var["load"][t],
                    name=f"neg_diff_load_{t}",
                )

        # Storage constraints if relevant
        if self.parameters.storage_exists:
            # Initial and final SOC constraints
            self.constr["initial_soc"] = self.model.addLConstr(
                self.var["SOC"][0],
                GRB.EQUAL,
                self.parameters.initial_soc
                * (
                    self.var["battery_scaling"]
                    if self.parameters.battery_size_variable
                    else 1
                ),
                name="initial_soc",
            )
            self.constr["final_soc"] = self.model.addLConstr(
                self.var["SOC"][self.parameters.T - 1],
                GRB.EQUAL,
                self.parameters.final_soc
                * (
                    self.var["battery_scaling"]
                    if self.parameters.battery_size_variable
                    else 1
                ),
                name="final_soc",
            )

            for t in range(1, self.parameters.T):
                # SOC balance constraint
                self.constr[f"soc_balance_{t}"] = self.model.addLConstr(
                    self.var["SOC"][t],
                    GRB.EQUAL,
                    self.var["SOC"][t - 1]
                    + self.parameters.charging_efficiency * self.var["charge"][t - 1]
                    - (1 / self.parameters.discharging_efficiency)
                    * self.var["discharge"][t - 1],
                    name=f"soc_balance_{t}",
                )

                # Charge and discharge capacity constraints
                self.constr[f"charge_capacity_{t}"] = self.model.addLConstr(
                    self.var["charge"][t],
                    GRB.LESS_EQUAL,
                    self.parameters.charging_capacity
                    * (
                        self.var["battery_scaling"]
                        if self.parameters.battery_size_variable
                        else 1
                    ),
                    name=f"charge_capacity_{t}",
                )
                self.constr[f"discharge_capacity_{t}"] = self.model.addLConstr(
                    self.var["discharge"][t],
                    GRB.LESS_EQUAL,
                    self.parameters.discharging_capacity
                    * (
                        self.var["battery_scaling"]
                        if self.parameters.battery_size_variable
                        else 1
                    ),
                    name=f"discharge_capacity_{t}",
                )

                # SOC capacity constraint
                self.constr[f"soc_capacity_{t}"] = self.model.addLConstr(
                    self.var["SOC"][t],
                    GRB.LESS_EQUAL,
                    self.parameters.storage_capacity
                    * (
                        self.var["battery_scaling"]
                        if self.parameters.battery_size_variable
                        else 1
                    ),
                    name=f"soc_capacity_{t}",
                )

        # Update model to integrate new constraints
        self.model.update()
        self.status += "\nConstraints added"


# Testing
if __name__ == "__main__":
    model = Optimization_model()
    print(model.status)
    model.load_data("question_1a")
    print(model.status)
