import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("timings.csv")
df2 = pd.read_csv("timings2.csv")

print(df["time"][0] - df["time"].iloc[-1])
print(sum(df["bytes"]) / (df["time"][0] - df["time"].iloc[-1]))
print(sum(df2["bytes"]) / (df2["time"][0] - df2["time"].iloc[-1]))

df["speed_ma"] = df["speed"].rolling(window=20, min_periods=1).mean()
plt.plot(df["time"] - df["time"][0], df["speed"]/1000)
plt.plot(df["time"] - df["time"].iloc[0], df["speed_ma"]/1000, label="Moving Average (5)", linewidth=2)
plt.plot(df2["time"] - df2["time"][0], df2["speed"]/1000)
plt.ylabel("Speed (kbps)")
plt.xlabel("Time")
plt.grid()
plt.show()
