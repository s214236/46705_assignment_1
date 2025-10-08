"""Main function to run the analysis."""

from Assignment_1_Classes.Optimization_model import Optimization_model
import numpy as np
from gurobipy import GRB
import matplotlib.pyplot as plt

question = "2b"  # Change this to run different questions

# %% Question 1a
if question == "1a":
    model = Optimization_model()
    model.load_data("question_1a")
    model.create_model()
    model.optimize()
    model.plot_results()

# %% Question 1b
if question == "1b":
    model = Optimization_model()
    model.load_data("question_1b")
    model.parameters.diff_penalty = 1.75
    model.create_model()
    model.optimize()
    model.plot_results()

# %% Question 1c
if question == "1c":
    model = Optimization_model()
    model.load_data("question_1c")
    model.parameters.diff_penalty = 1.75
    model.create_model()
    model.optimize()
    model.plot_results()

# %% Question 2b
if question == "2b":
    model = Optimization_model()
    model.load_data("question_2b")
    model.parameters.diff_penalty = GRB.INFINITY
    model.set_battery_size_as_variable()

    battery_prices = np.arange(3, 10, 0.1)
    battery_size = []
    objective_value = []
    for battery_cost in battery_prices:
        model.parameters.battery_cost = battery_cost
        model.create_model()
        model.optimize()
        results = model.get_results()
        battery_size.append(results["battery_size"])
        objective_value.append(results["objective_value"])

    fig, ax1 = plt.subplots()

    color = "tab:blue"
    ax1.set_xlabel("Battery Price")
    ax1.set_ylabel("Battery Size", color=color)
    ax1.plot(battery_prices, battery_size, color=color, label="Battery Size")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Objective Value", color=color)
    ax2.plot(battery_prices, objective_value, color=color, label="Objective Value")
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.title("Battery Size and Objective Value vs Battery Price")
    plt.show()
