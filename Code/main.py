import numpy as np
import gurobipy as gp
from gurobipy import GRB
from read_data import load_datasets
import matplotlib.pyplot as plt

# %% Settings
question = "question_1b"

# %% Loading data
Parameters = load_datasets(question)

PV_params = Parameters["appliance_params.json"]["DER"][0]
load_params = Parameters["appliance_params.json"]["load"][0]
# storage_list = Parameters["appliance_params.json"]["storage"]
# heat_pump_list = Parameters["appliance_params.json"]["heat_pump"]
bus_params = Parameters["bus_params.json"][0]
production_params = Parameters["DER_production.json"][0]
usage_params = Parameters["usage_preferences.json"][0]

# %% Setting parameters
T = len(bus_params["energy_price_DKK_per_kWh"])  # Number of hours
PV_max = PV_params["max_power_kW"] * np.array(
    production_params["hourly_profile_ratio"]
)  # Max PV power per hour
load_max = load_params["max_load_kWh_per_hour"]  # Max load per hour
import_max = bus_params["max_import_kW"]  # Max import power
export_max = bus_params["max_export_kW"]  # Max export power
import_price = (
    np.array(bus_params["energy_price_DKK_per_kWh"])
    + bus_params["import_tariff_DKK/kWh"]
)  # Cost for import
export_price = (
    np.array(bus_params["energy_price_DKK_per_kWh"])
    - bus_params["export_tariff_DKK/kWh"]
)  # Revenue for export
excess_import_cost = bus_params[
    "penalty_excess_import_DKK/kWh"
]  # Cost for excess import
excess_export_cost = bus_params[
    "penalty_excess_export_DKK/kWh"
]  # Cost for excess export
min_combined_load = usage_params["load_preferences"][0][
    "min_total_energy_per_day_hour_equivalent"
]  # Minimum combined load per day
if usage_params["load_preferences"][0]["hourly_profile_ratio"] is not None:
    desired_load = (
        np.array(usage_params["load_preferences"][0]["hourly_profile_ratio"]) * load_max
    )  # Desired load profile
else:
    desired_load = None
diff_penalty = 1.75

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

# Then the variables are added to the model using a loop
# Note: the upper and lower bounds are added here as well instead of using a specific constraint
for t in range(T):
    load_var[t] = model.addVar(name=f"load_{t}", lb=0, ub=load_max)
    gen_var[t] = model.addVar(name=f"gen_{t}", lb=0, ub=PV_max[t])
    import_var[t] = model.addVar(name=f"import_{t}", lb=0)
    export_var[t] = model.addVar(name=f"export_{t}", lb=0)
    excess_import_var[t] = model.addVar(name=f"excess_import_{t}", lb=0)
    excess_export_var[t] = model.addVar(name=f"excess_export_{t}", lb=0)
    pos_diff_load_var[t] = model.addVar(name=f"pos_diff_load_{t}", lb=0)
    neg_diff_load_var[t] = model.addVar(name=f"neg_diff_load_{t}", lb=0)

model.update()

# %% Objective
model.setObjective(
    gp.quicksum(
        import_price[t] * import_var[t]
        - export_price[t] * export_var[t]
        + excess_import_cost * excess_import_var[t]
        + excess_export_cost * excess_export_var[t]
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
        load_var[t] + export_var[t],
        GRB.EQUAL,
        gen_var[t] + import_var[t],
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

# Excess import and export constraints
for t in range(T):
    constraints[f"excess_import_{t}"] = model.addLConstr(
        excess_import_var[t],
        GRB.GREATER_EQUAL,
        import_var[t] - import_max,
        name=f"excess_import_{t}",
    )

    constraints[f"excess_export_{t}"] = model.addLConstr(
        excess_export_var[t],
        GRB.GREATER_EQUAL,
        export_var[t] - export_max,
        name=f"excess_export_{t}",
    )

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
    for t in range(T):
        load.append(model.getVarByName(f"load_{t}").x)
        PV_prod.append(model.getVarByName(f"gen_{t}").x)
        import_grid.append(model.getVarByName(f"import_{t}").x)
        export_grid.append(model.getVarByName(f"export_{t}").x)

    plt.figure()
    plt.plot(load, label="Load (kW)", color="blue")
    plt.plot(PV_prod, label="PV Production (kW)", color="orange")
    plt.plot(import_grid, label="Import from Grid (kW)", color="green", linestyle="--")
    plt.plot(export_grid, label="Export to Grid (kW)", color="red", linestyle="--")
    plt.plot(
        export_price, label="Electricity Price (DKK/kWh)", color="purple", linestyle=":"
    )
    if desired_load is not None:
        plt.plot(desired_load, label="Desired Load (kW)", color="cyan", linestyle="-.")
    plt.legend()
    plt.xlabel("Time (hours)")
    plt.ylabel("Power (kW)")
    plt.title("Energy System Optimization Results")
    plt.show()

else:
    print("No optimal solution found.")
