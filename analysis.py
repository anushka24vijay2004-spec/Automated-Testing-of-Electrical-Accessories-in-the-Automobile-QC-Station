import pandas as pd
import matplotlib.pyplot as plt

# File ko manually split karne ke liye
df = pd.read_csv("vehicle_raw_data.csv")

# Agar sirf 1 column aa raha ho toh manually split karo
if len(df.columns) == 1:
    df = df[df.columns[0]].str.split(",", expand=True)
    df.columns = ["timestamp", "vehicle_id", "accessory", "current", "lux", "sound"]

# Data type convert karo
df["current"] = pd.to_numeric(df["current"])
df["sound"] = pd.to_numeric(df["sound"])

print("Columns:", df.columns)

# -----------------------
# CURRENT GRAPH
# -----------------------
plt.figure()
plt.plot(df["current"])
plt.title("Current vs Time")
plt.xlabel("Sample Number")
plt.ylabel("Current (A)")
plt.grid(True)
plt.show()

# -----------------------
# SOUND GRAPH
# -----------------------
plt.figure()
plt.plot(df["sound"])
plt.title("Sound vs Time")
plt.xlabel("Sample Number")
plt.ylabel("Sound Level")
plt.grid(True)
plt.show()