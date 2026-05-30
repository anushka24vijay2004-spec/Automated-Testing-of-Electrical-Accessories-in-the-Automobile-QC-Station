from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

CSV_FILE = "central_qc_database.csv"


# CSV file create if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp",
            "Avg Voltage",
            "Avg Current",
            "Avg Power",
            "Voltage Drop",
            "Peak Current",
            "Avg Lux",
            "Sound Variation",
            "Final Status"
        ])


@app.route('/')
def home():
    return "🏭 SFS Central Server Running"


# TSS se data receive
@app.route('/store_result', methods=['POST'])
def store_result():

    data = request.get_json()

    print("\n📥 NEW DATA RECEIVED FROM TSS")
    print("Timestamp :", data.get("timestamp"))
    print("Voltage   :", data.get("avg_voltage"))
    print("Current   :", data.get("avg_current"))
    print("Power     :", data.get("avg_power"))
    print("Lux       :", data.get("avg_lux"))
    print("Sound Var :", data.get("sound_variation"))
    print("Status    :", data.get("final_status"))

    with open(CSV_FILE, 'a', newline='') as f:

        writer = csv.writer(f)

        writer.writerow([
            data.get("timestamp"),
            data.get("avg_voltage"),
            data.get("avg_current"),
            data.get("avg_power"),
            data.get("voltage_drop"),
            data.get("peak_current"),
            data.get("avg_lux"),
            data.get("sound_variation"),
            data.get("final_status")
        ])

    print("✅ Data stored in central_qc_database.csv")

    return jsonify({"status": "stored"})


if __name__ == "__main__":
    print("🏭 SFS SERVER RUNNING ON PORT 5001")
    app.run(host="0.0.0.0", port=5001)