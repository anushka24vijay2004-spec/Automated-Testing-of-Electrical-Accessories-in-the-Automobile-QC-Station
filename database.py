import pandas as pd
import os

FILE_NAME = "vehicle_data.csv"

def save_to_csv(data):

    df = pd.DataFrame([data])   # JSON ko DataFrame me convert

    # Agar file already exist karti hai
    if os.path.exists(FILE_NAME):
        df.to_csv(FILE_NAME, mode='a', header=False, index=False)
    else:
        df.to_csv(FILE_NAME, mode='w', header=True, index=False)

    print("Data Saved Successfully ✅")