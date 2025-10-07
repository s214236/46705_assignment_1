import numpy as np
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
from Code.Parameters import Parameters


class Optimization_model:
    def __init__(self):
        self.status = "Empty model"

    def load_data(self, dataset_folder: str):
        self.parameters = Parameters(dataset_folder)
        self.status = "Data loaded"


if __name__ == "__main__":
    model = Optimization_model()
    print(model.status)
    model.load_data("question_1a")
    print(model.status)

"""
# %% Setting parameters


# %% Model initialization
model = gp.Model("Energy System Optimization")

# %% Variables
# First, a dictionary for each variable is created to contain variables for all hours
load_var = {}
gen_var = {}
import_var = {}
export_var = {}
excess_import_var = {}
excess_export_var = {}
pos_diff_load_var = {}
neg_diff_load_var = {}
discharge_var = {}
charge_var = {}
SOC_var = {}

# Then the variables are added to the model using a loop
# Note: the upper and lower bounds are added here as well instead of using a specific constraint
for t in range(T):
    load_var[t] = model.addVar(name=f"load_{t}", lb=0, ub=load_max)
    gen_var[t] = model.addVar(name=f"gen_{t}", lb=0, ub=PV_max[t])
    import_var[t] = model.addVar(name=f"import_{t}", lb=0)
    export_var[t] = model.addVar(name=f"export_{t}", lb=0)
    pos_diff_load_var[t] = model.addVar(name=f"pos_diff_load_{t}", lb=0)
    neg_diff_load_var[t] = model.addVar(name=f"neg_diff_load_{t}", lb=0)
    if storage:
        discharge_var[t] = model.addVar(
            name=f"discharge_{t}", lb=0, ub=discharging_capacity
        )
        charge_var[t] = model.addVar(name=f"charge_{t}", lb=0, ub=charging_capacity)
        SOC_var[t] = model.addVar(name=f"SOC_{t}", lb=0, ub=storage_capacity)

model.update()

# %% Objective
model.setObjective(
    gp.quicksum(
        import_price[t] * import_var[t]
        - export_price[t] * export_var[t]
        + diff_penalty * (pos_diff_load_var[t] + neg_diff_load_var[t])
        for t in range(T)
    ),
    GRB.MINIMIZE,
)

model.update()

# %% Constraints
constraints = {}
# Energy balance constraint
for t in range(T):
    constraints[f"energy_balance_{t}"] = model.addLConstr(
        load_var[t] + export_var[t] + (charge_var[t] if storage else 0),
        GRB.EQUAL,
        gen_var[t] + import_var[t] + (discharge_var[t] if storage else 0),
        name=f"energy_balance_{t}",
    )

# Minimum combined load constraint
if min_combined_load is not None:
    constraints[f"minimum_combined_load"] = model.addLConstr(
        gp.quicksum(load_var[t] for t in range(T)),
        GRB.GREATER_EQUAL,
        min_combined_load,
        name="minimum_combined_load",
    )


# Desired load profile constraints
if desired_load is not None:
    for t in range(T):
        constraints[f"pos_diff_load_{t}"] = model.addLConstr(
            pos_diff_load_var[t],
            GRB.GREATER_EQUAL,
            load_var[t] - desired_load[t],
            name=f"pos_diff_load_{t}",
        )
        constraints[f"neg_diff_load_{t}"] = model.addLConstr(
            neg_diff_load_var[t],
            GRB.GREATER_EQUAL,
            desired_load[t] - load_var[t],
            name=f"neg_diff_load_{t}",
        )

# Storage constraints
if storage:
    constraints[f"initial_soc"] = model.addLConstr(
        SOC_var[0],
        GRB.EQUAL,
        initial_soc,
        name="initial_soc",
    )
    constraints[f"final_soc"] = model.addLConstr(
        SOC_var[T - 1],
        GRB.EQUAL,
        final_soc,
        name="final_soc",
    )
    for t in range(1, T):
        constraints[f"soc_balance_{t}"] = model.addLConstr(
            SOC_var[t],
            GRB.EQUAL,
            SOC_var[t - 1]
            + charging_efficiency * charge_var[t - 1]
            - (1 / discharging_efficiency) * discharge_var[t - 1],
            name=f"soc_balance_{t}",
        )

model.update()

# %% Optimize model
model.optimize()

# %% Check status and plot results
if model.status == GRB.OPTIMAL:
    optimal_objective = model.ObjVal
    print(f"optimal objective: {optimal_objective}")

    load = []
    PV_prod = []
    import_grid = []
    export_grid = []
    charge = []
    discharge = []
    soc = []
    for t in range(T):
        load.append(model.getVarByName(f"load_{t}").x)
        PV_prod.append(model.getVarByName(f"gen_{t}").x)
        import_grid.append(model.getVarByName(f"import_{t}").x)
        export_grid.append(model.getVarByName(f"export_{t}").x)
        charge.append(model.getVarByName(f"charge_{t}").x if storage else 0)
        discharge.append(model.getVarByName(f"discharge_{t}").x if storage else 0)
        soc.append(model.getVarByName(f"SOC_{t}").x if storage else 0)

    index_list = np.arange(24)

    plt.figure()
    plt.step(index_list, load, label="Load (kW)", color="blue", where="post")
    plt.step(
        index_list, PV_prod, label="PV Production (kW)", color="orange", where="post"
    )
    plt.step(
        index_list,
        import_grid,
        label="Import from Grid (kW)",
        color="green",
        linestyle="--",
        where="post",
    )
    plt.step(
        index_list,
        export_grid,
        label="Export to Grid (kW)",
        color="red",
        linestyle="--",
        where="post",
    )
    plt.step(
        index_list,
        electricity_price,
        label="Electricity Price (DKK/kWh)",
        color="purple",
        linestyle=":",
        where="post",
    )
    if desired_load is not None:
        plt.step(
            index_list,
            desired_load,
            label="Desired Load (kW)",
            color="cyan",
            linestyle="-.",
            where="post",
        )
    if storage:
        plt.step(
            index_list,
            charge,
            label="Storage Charge (kW)",
            color="brown",
            linestyle=":",
            where="post",
        )
        plt.step(
            index_list,
            discharge,
            label="Storage Discharge (kW)",
            color="pink",
            linestyle=":",
            where="post",
        )
        plt.plot(soc, label="Storage SOC (kWh)", color="gray", linestyle="--")
    plt.legend()
    plt.xlabel("Time (hours)")
    plt.ylabel("Power (kW)")
    plt.title("Energy System Optimization Results")
    plt.show()


else:
    print("No optimal solution found.")
"""
