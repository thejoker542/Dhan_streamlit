import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import os 

df = pd.read_csv("/workspaces/Dhan_streamlit/backend/data/test_straddle_NIFTY2510923450CE.csv")
df.plot(x="date", y="straddle_price")
plt.savefig("/workspaces/Dhan_streamlit/backend/data/straddle_price_plot.png")