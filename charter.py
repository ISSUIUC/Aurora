import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("timings.csv")

plt.plot(df["time"], df["bytes"])
plt.ylabel("Speed (kbps)")
plt.xlabel("Time")
plt.grid()
plt.show()
