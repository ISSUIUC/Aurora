import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("timings.csv")
df2 = pd.read_csv("timings2.csv")

plt.plot(df["time"] - df["time"][0], df["speed"]/1000)
plt.plot(df2["time"] - df2["time"][0], df2["speed"]/1000)
plt.ylabel("Speed (kbps)")
plt.xlabel("Time")
plt.grid()
plt.show()
