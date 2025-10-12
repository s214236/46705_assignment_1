"""Main function to run the analysis."""

from Assignment_1_Classes.Optimization_model import Optimization_model
import numpy as np
from gurobipy import GRB
import matplotlib.pyplot as plt

question = "2b"  # Change this to run different questions

# Questions are run in general using the following structure:
model = Optimization_model()
model.load_data(f"question_{question}")
model.create_model()
model.optimize()
model.plot_results()
results = model.get_results()

# In the below different scenarios are plotted with mulitple runs of the model

# %% Question 1a
if question == "1a":
    # Run model and plot results
    model = Optimization_model()
    model.load_data("question_1a")
    model.create_model()
    model.optimize()
    base_obj = model.get_results()["objective_value"]
    model.plot_results()

    # Analyze dual variables for different price factors
    duals_dict = {}
    objective_values_factor = {}
    price_factors = np.arange(0.25, 2.25, 0.25)
    for factor in price_factors:
        model = Optimization_model()
        model.load_data("question_1a")
        model.parameters.export_price = factor * model.parameters.export_price
        model.parameters.import_price = factor * model.parameters.import_price
        model.create_model()
        model.optimize()
        results = model.get_results()
        duals_dict[factor] = list(results["duals"].values())[:-1]
        objective_values_factor[factor] = results["objective_value"]

    plt.figure()
    for i, (key, duals) in enumerate(duals_dict.items()):
        plt.plot(duals, label=f"Price Factor: {key}")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title(
        "Dual variables of the energy balance constraints for different price factors"
    )
    plt.legend()
    plt.grid()
    plt.show()

    # Analyze dual variables for different scales of flat prices
    duals_dict = {}
    objective_values_flat_factors = {}
    price_factors = np.arange(0.25, 2.25, 0.25)
    for factor in price_factors:
        model = Optimization_model()
        model.load_data("question_1a")
        model.parameters.export_price = (
            np.ones(model.parameters.T)
            * np.mean(model.parameters.export_price)
            * factor
        )
        model.parameters.import_price = (
            np.ones(model.parameters.T)
            * np.mean(model.parameters.import_price)
            * factor
        )
        model.create_model()
        model.optimize()
        results = model.get_results()
        duals_dict[factor] = list(results["duals"].values())[:-1]
        objective_values_flat_factors[factor] = results["objective_value"]

    plt.figure()
    for i, (key, duals) in enumerate(duals_dict.items()):
        plt.plot(duals, label=f"Price Factor: {key}")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title(
        "Dual variables of the energy balance constraints for different flat price factors"
    )
    plt.legend()
    plt.grid()
    plt.show()

    print("Base Objective Value:", base_obj)
    print("Objective Values (Price Factors):", objective_values_factor)
    print("Objective Values (Flat Price Factors):", objective_values_flat_factors)

    plt.figure()
    plt.plot(
        list(objective_values_factor.keys()),
        list(objective_values_factor.values()),
        label="Scaled Prices",
    )
    plt.plot(
        list(objective_values_flat_factors.keys()),
        list(objective_values_flat_factors.values()),
        label="Flat Prices",
    )
    plt.xlabel("Price Factor")
    plt.ylabel("Objective Value")
    plt.title("Objective Values for Different Price Factors")
    plt.grid()
    plt.legend()
    plt.show()

# %% Question 1b
if question == "1b":
    model = Optimization_model()
    model.load_data("question_1b")
    model.create_model()
    model.optimize()
    model.plot_results()

    diff_penalties = np.arange(0, 5, 0.01)
    objective_values = {}
    for penalty in diff_penalties:
        model = Optimization_model()
        model.load_data("question_1b")
        model.parameters.diff_penalty = penalty
        model.create_model()
        model.optimize()
        results = model.get_results()
        objective_values[penalty] = results["objective_value"]

    plt.figure()
    plt.plot(
        list(objective_values.keys()),
        list(objective_values.values()),
        label="Objective Value vs Diff Penalty",
    )
    plt.xlabel("Deviation Penalty")
    plt.ylabel("Objective Value")
    plt.title("Objective Value vs Differentiation Penalty")
    plt.grid()
    plt.legend()
    plt.show()

    model = Optimization_model()
    model.load_data("question_1b")
    model.parameters.diff_penalty = 1.75
    model.create_model()
    model.optimize()
    model.plot_results()

    results = model.get_results()
    # Extract duals for pos_diff_load and neg_diff_load constraints
    pos_diff_duals = [v for k, v in results["duals"].items() if "pos_diff_load" in k]
    neg_diff_duals = [v for k, v in results["duals"].items() if "neg_diff_load" in k]
    plt.figure()
    plt.plot(pos_diff_duals, label="positive_diff_load duals")
    plt.plot(neg_diff_duals, label="negative_diff_load duals")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title("Dual variables of the desired load constraints")
    plt.grid()
    plt.legend()
    plt.show()

# %% Question 1c
if question == "1c":
    model = Optimization_model()
    model.load_data("question_1c")
    model.create_model()
    model.optimize()
    model.plot_results()

    # Analyze dual variables for different price factors
    duals_dict = {}
    objective_values_factor = {}
    price_factors = np.arange(0.25, 2.25, 0.25)
    for factor in price_factors:
        model = Optimization_model()
        model.load_data("question_1c")
        model.parameters.export_price = factor * model.parameters.export_price
        model.parameters.import_price = factor * model.parameters.import_price
        model.create_model()
        model.optimize()
        results = model.get_results()
        duals_dict[factor] = list(results["duals"].values())[:24]
        objective_values_factor[factor] = results["objective_value"]

    plt.figure()
    for i, (key, duals) in enumerate(duals_dict.items()):
        plt.plot(duals, label=f"Price Factor: {key}")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title(
        "Dual variables of the energy balance constraints for different price factors"
    )
    plt.legend()
    plt.grid()
    plt.show()

    # Analyze dual variables for different scales of flat prices
    duals_dict = {}
    objective_values_flat_factors = {}
    price_factors = np.arange(0.25, 2.25, 0.25)
    for factor in price_factors:
        model = Optimization_model()
        model.load_data("question_1c")
        model.parameters.export_price = (
            np.ones(model.parameters.T)
            * np.mean(model.parameters.export_price)
            * factor
        )
        model.parameters.import_price = (
            np.ones(model.parameters.T)
            * np.mean(model.parameters.import_price)
            * factor
        )
        model.create_model()
        model.optimize()
        results = model.get_results()
        duals_dict[factor] = list(results["duals"].values())[:24]
        objective_values_flat_factors[factor] = results["objective_value"]

    plt.figure()
    for i, (key, duals) in enumerate(duals_dict.items()):
        plt.plot(duals, label=f"Price Factor: {key}")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title(
        "Dual variables of the energy balance constraints for different flat price factors"
    )
    plt.legend()
    plt.grid()
    plt.show()

    print("Objective Values (Price Factors):", objective_values_factor)
    print("Objective Values (Flat Price Factors):", objective_values_flat_factors)

    plt.figure()
    plt.plot(
        list(objective_values_factor.keys()),
        list(objective_values_factor.values()),
        label="Scaled Prices",
    )
    plt.plot(
        list(objective_values_flat_factors.keys()),
        list(objective_values_flat_factors.values()),
        label="Flat Prices",
    )
    plt.xlabel("Price Factor")
    plt.ylabel("Objective Value")
    plt.title("Objective Values for Different Price Factors")
    plt.grid()
    plt.legend()
    plt.show()

    diff_penalties = np.arange(0, 5, 0.01)
    objective_values = {}
    for penalty in diff_penalties:
        model = Optimization_model()
        model.load_data("question_1c")
        model.parameters.diff_penalty = penalty
        model.create_model()
        model.optimize()
        results = model.get_results()
        objective_values[penalty] = results["objective_value"]

    plt.figure()
    plt.plot(
        list(objective_values.keys()),
        list(objective_values.values()),
        label="Objective Value vs Diff Penalty",
    )
    plt.xlabel("Deviation Penalty")
    plt.ylabel("Objective Value")
    plt.title("Objective Value vs Differentiation Penalty")
    plt.grid()
    plt.legend()
    plt.show()

    model = Optimization_model()
    model.load_data("question_1c")
    model.parameters.diff_penalty = 1.75
    model.create_model()
    model.optimize()
    model.plot_results()

    results = model.get_results()
    # Extract duals for pos_diff_load and neg_diff_load constraints
    pos_diff_duals = [v for k, v in results["duals"].items() if "pos_diff_load" in k]
    neg_diff_duals = [v for k, v in results["duals"].items() if "neg_diff_load" in k]
    plt.figure()
    plt.plot(pos_diff_duals, label="positive_diff_load duals")
    plt.plot(neg_diff_duals, label="negative_diff_load duals")
    plt.xlabel("Time (hours)")
    plt.ylabel("Shadow Price (DKK/kWh)")
    plt.title("Dual variables of the desired load constraints")
    plt.grid()
    plt.legend()
    plt.show()

# %% Question 2b
if question == "2b":

    model = Optimization_model()
    model.load_data("question_2b")
    model.set_battery_size_as_variable()
    model.parameters.battery_cost = 5  # DKK/kWh
    model.create_model()
    model.optimize()
    model.plot_results()

    # Battery Size and Objective Value vs Battery Price
    battery_prices = np.arange(3, 10, 0.01)
    battery_size = {}
    objective_value = {}
    for battery_cost in battery_prices:
        model = Optimization_model()
        model.load_data("question_2b")
        model.set_battery_size_as_variable()
        model.parameters.battery_cost = battery_cost
        model.create_model()
        model.optimize()
        results = model.get_results()
        battery_size[battery_cost] = results["battery_size"]
        objective_value[battery_cost] = results["objective_value"]

    fig, ax1 = plt.subplots()

    color = "tab:blue"
    ax1.set_xlabel("Battery Price")
    ax1.set_ylabel("Battery Size", color=color)
    ax1.plot(
        battery_size.keys(), battery_size.values(), color=color, label="Battery Size"
    )
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Objective Value", color=color)
    ax2.plot(
        objective_value.keys(),
        objective_value.values(),
        color=color,
        label="Objective Value",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.title("Battery Size and Objective Value vs Battery Price")
    plt.show()

    # Battery Size and Objective Value vs Battery Price with flat prices
    battery_prices = np.arange(3, 10, 0.01)
    battery_size = {}
    objective_value = {}
    for battery_cost in battery_prices:
        model = Optimization_model()
        model.load_data("question_2b")
        model.set_battery_size_as_variable()
        model.parameters.export_price = np.ones(model.parameters.T) * np.mean(
            model.parameters.export_price
        )
        model.parameters.import_price = np.ones(model.parameters.T) * np.mean(
            model.parameters.import_price
        )
        model.parameters.battery_cost = battery_cost
        model.create_model()
        model.optimize()
        results = model.get_results()
        battery_size[battery_cost] = results["battery_size"]
        objective_value[battery_cost] = results["objective_value"]

    fig, ax1 = plt.subplots()

    color = "tab:blue"
    ax1.set_xlabel("Battery Price")
    ax1.set_ylabel("Battery Size", color=color)
    ax1.plot(
        battery_size.keys(), battery_size.values(), color=color, label="Battery Size"
    )
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Objective Value", color=color)
    ax2.plot(
        objective_value.keys(),
        objective_value.values(),
        color=color,
        label="Objective Value",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.title("Battery Size and Objective Value vs Battery Price")
    plt.show()
