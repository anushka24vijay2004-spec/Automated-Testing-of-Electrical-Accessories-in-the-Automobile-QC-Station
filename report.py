import pandas as pd
from datetime import datetime


def generate_vehicle_report(vehicle_id):

    df = pd.read_csv("vehicle_data.csv", engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()

    vehicle_df = df[df.iloc[:, 0] == vehicle_id]

    if vehicle_df.empty:
        print("❌ No data found for this vehicle.")
        return

    # Assume last column = status if exists
    if len(df.columns) >= 7:
        status_column = df.columns[-1]
    else:
        print("⚠ Status column not found. Using default PASS.")
        vehicle_df["Status"] = "PASS"
        status_column = "Status"

    # Overall final status logic
    if "EMERGENCY" in vehicle_df[status_column].astype(str).values:
        overall_status = "EMERGENCY"
    elif "FAIL" in vehicle_df[status_column].astype(str).values:
        overall_status = "FAIL"
    elif "WARNING" in str(vehicle_df[status_column].values):
        overall_status = "WARNING"
    else:
        overall_status = "PASS"

    # Save detailed report
    filename = f"vehicle_{vehicle_id}_report.csv"
    vehicle_df.to_csv(filename, index=False)

    print(f"✅ Detailed Report Generated: {filename}")
    print(f"🚗 Overall Vehicle Status: {overall_status}")


if __name__ == "__main__":
    print("🚀 Report script started...")
    generate_vehicle_report(101)