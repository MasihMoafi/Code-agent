#!/usr/bin/env python
# coding: utf-8

# <table align="left">
#   <tr>
#  <td><img src="icecreamtruck.jpeg" alt="Ice Cream Truck" width="150"/></td>
#  <td align="left"><h1>Lesson 2: Introduction to Code Agents</h1></td>

# <div style="background-color:#fff6ff; padding:13px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px">
# <p> 💻 &nbsp; <b>Access <code>requirements.txt</code>  file:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>.
# 
# <p> ⬇ &nbsp; <b>Download Notebooks:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Download as"</em> and select <em>"Notebook (.ipynb)"</em>.</p>
# 
# <p> 📒 &nbsp; For more help, please see the <em>"Appendix – Tips, Help, and Download"</em> Lesson.</p>
# 
# </div>

# <p style="background-color:#f7fff8; padding:15px; border-width:3px; border-color:#e0f0e0; border-style:solid; border-radius:6px"> 🚨
# &nbsp; <b>Different Run Results:</b> The output generated by AI chat models can vary with each execution due to their dynamic, probabilistic nature. Don't be surprised if your results differ from those shown in the video.</p>

# In[ ]:


# Warning control
import warnings

warnings.filterwarnings("ignore")

import os
import io
import IPython.display
from PIL import Image
import base64

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv() # read local .env file

from huggingface_hub import login

login(os.environ['HF_API_KEY'])


# In[ ]:


import pandas as pd

suppliers_data = {
    "name": [
        "Montreal Ice Cream Co",
        "Brain Freeze Brothers",
        "Toronto Gelato Ltd",
        "Buffalo Scoops",
        "Vermont Creamery",
    ],
    "location": [
        "Montreal, QC",
        "Burlington, VT",
        "Toronto, ON",
        "Buffalo, NY",
        "Portland, ME",
    ],
    "distance_km": [120, 85, 400, 220, 280],
    "canadian": [True, False, True, False, False],
    "price_per_liter": [1.95, 1.91, 1.82, 2.43, 2.33],
    "tasting_fee": [0, 12.50, 30.14, 42.00, 0.20],
}

data_description = """Suppliers have an additional tasting fee: that is a fixed fee applied to each order to taste the ice cream."""
suppliers_df = pd.DataFrame(suppliers_data)
suppliers_df


# ## Setup tools

# In[ ]:


import numpy as np

def calculate_daily_supplier_price(row):
    order_volume = 30

    # Calculate raw product cost
    product_cost = row["price_per_liter"] * order_volume

    # Calculate transport cost
    trucks_needed = np.ceil(order_volume / 300)
    cost_per_km = 1.20
    transport_cost = row["distance_km"] * cost_per_km * trucks_needed

    # Calculate tariffs for ice cream imported from Canada
    tariff = product_cost * np.pi / 50 * row["canadian"]

    # Get total cost
    total_cost = product_cost + transport_cost + tariff + row["tasting_fee"]
    return total_cost

suppliers_df["daily_price"] = suppliers_df.apply(calculate_daily_supplier_price, axis=1)
display(suppliers_df)

# Let's remove this column now.
suppliers_df = suppliers_df.drop("daily_price", axis=1)


# In[ ]:


# First we make a few tools
from smolagents import tool

@tool
def calculate_transport_cost(distance_km: float, order_volume: float) -> float:
    """
    Calculate transportation cost based on distance and order size.
    Refrigerated transport costs $1.2 per kilometer and has a capacity of 300 liters.

    Args:
        distance_km: the distance in kilometers
        order_volume: the order volume in liters
    """
    trucks_needed = np.ceil(order_volume / 300)
    cost_per_km = 1.20
    return distance_km * cost_per_km * trucks_needed


@tool
def calculate_tariff(base_cost: float, is_canadian: bool) -> float:
    """
    Calculates tariff for Canadian imports. Returns the tariff only, not the total cost.
    Assumes tariff on dairy products from Canada is worth 2 * pi / 100, approx 6.2%

    Args:
        base_cost: the base cost of goods, not including transportation cost.
        is_canadian: wether the import is from Canada.
    """
    if is_canadian:
        return base_cost * np.pi / 50
    return 0


# In[ ]:


calculate_transport_cost.description


# ## Setup the Model

# In[ ]:


from smolagents import HfApiModel, CodeAgent
from helper import get_huggingface_token

model = HfApiModel(
    "Qwen/Qwen2.5-72B-Instruct",
    provider="together", # Choose a specific inference provider
    max_tokens=4096,
    temperature=0.1
)


# ## Setup the Code Agent

# In[ ]:


agent = CodeAgent(
    model=model,
    tools=[calculate_transport_cost, calculate_tariff],
    max_steps=10,
    additional_authorized_imports=["pandas", "numpy"],
    verbosity_level=2
)
agent.logger.console.width=66


# In[ ]:


agent.run(
    """Can you get me the transportation cost for 50 liters
    of ice cream over 10 kilometers?"""
)


# ## Give the agent detailed instructions

# In[ ]:


task = """Here is a dataframe of different ice cream suppliers.
Could you give me a comparative table (as a dataframe) of the total
daily price for getting daily ice cream delivery from each of them,
given that we need exactly 30 liters of ice cream per day? Take
into account transportation cost and tariffs.
"""
agent.logger.level = 1 # Lower verbosity level
agent.run(
    task,
    additional_args={"suppliers_data": suppliers_df, "data_description": data_description},
)


# ## Compare to traditional tool calling.
# Thought: I need to use the `calculate_transport_cost` tool
# to get the transportation cost for 50 liters of ice cream over
# 10 kilometers.
#                         
# Code:
# ```py                                  
# transport_cost = calculate_transport_cost(
#     distance_km=10,
#     order_volume=50
# )
# print(transport_cost)                             
# ```
#
# Thought: I need to use the `calculate_transport_cost` tool
# to get the transportation cost for 50 liters of ice cream over
# 10 kilometers.
#
# Action:
# {
#     "tool_name": "calculate_transport_cost",
#     "tool_arguments": {
#         "distance_km": 10,
#         "order_volume": 50
#     }
# }
# In[ ]:


from smolagents import ToolCallingAgent

model = HfApiModel(
    "Qwen/Qwen2.5-72B-Instruct",
    temperature=0.6
)
agent = ToolCallingAgent(
    model=model,
    tools=[calculate_transport_cost, calculate_tariff],
    max_steps=20,
)
agent.logger.console.width=66


# <div style="font-size: 14px; background-color: #fff9b0; padding: 12px; border-left: 4px solid #facc15;">
#   <strong>Note:</strong> During this run, the agent may generate code that creates an error. This is OK. The agent will try to fix the error.
# </div>
# 

# In[ ]:


output = agent.run(
    task,
    additional_args={"suppliers_data": suppliers_df, "data_description": data_description},
)
print(output)


# In[ ]:





# In[ ]:




