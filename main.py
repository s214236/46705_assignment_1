"""Main function to run the analysis."""

# # %% Question 1a
# from Code.Optimization_model import Optimization_model

# model = Optimization_model()
# model.load_data("question_1a")
# model.create_model()
# model.optimize()
# model.plot_results()

# # %% Question 1b
# from Code.Optimization_model import Optimization_model

# model = Optimization_model()
# model.load_data("question_1b")
# model.parameters.diff_penalty = 1.75
# model.create_model()
# model.optimize()
# model.plot_results()

# # %% Question 1c
# from Code.Optimization_model import Optimization_model

# model = Optimization_model()
# model.load_data("question_1c")
# model.parameters.diff_penalty = 1.75
# model.create_model()
# model.optimize()
# model.plot_results()

# %% Question 2b
from Code.Optimization_model import Optimization_model

model = Optimization_model()
model.load_data("question_2b")
model.parameters.diff_penalty = 1.75
model.set_battery_size_as_variable()
model.parameters.battery_cost = 10
model.create_model()
model.optimize()
model.plot_results()

# %%
