from flask import Flask, request, jsonify
from datetime import datetime
import json
import csv
import os
import requests

app = Flask(__name__)

# -------- CONFIG --------
SAMPLE_LIMIT = 5
capture_mode = False
capture_buffer = []
last_result = None
CSV_FILE = "qc_report.csv"

# -------- CREATE CSV --------
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

# -------- HOME --------
@app.route('/')
def home():
    return "🚗 TSS Server Running"

# -------- START CAPTURE --------#
@app.route('/start_capture', methods=['GET','POST'])
def start_capture():
    global capture_mode, capture_buffer
    capture_mode = True
    capture_buffer = []
    print("🔒 Capture Mode Started")
    return jsonify({"status": "capture_started"})


# -------- RECEIVE DATA FROM ESP32 --------
@app.route('/data', methods=['POST'])
def receive_data():
    global capture_mode, capture_buffer, last_result

    data = request.get_json()

    print("📥 Data Received:", data)

    if capture_mode:

        capture_buffer.append(data)
        print(f"Sample {len(capture_buffer)}/{SAMPLE_LIMIT}")

        if len(capture_buffer) >= SAMPLE_LIMIT:

            last_result = analyze_data(capture_buffer)

            capture_buffer = []
            capture_mode = False

            return jsonify({
                "status": "analysis_complete",
                "result": last_result
            })

    return jsonify({"status": "collecting"})


# -------- ANALYSIS --------
def analyze_data(buffer):

    voltages = [d["voltage"] for d in buffer]
    currents = [d["current"] for d in buffer]
    powers = [d["power"] for d in buffer]
    lux_values = [d["lux"] for d in buffer]
    sound_values = [d["sound"] for d in buffer]

    avg_voltage = sum(voltages) / len(voltages)
    avg_current = sum(currents) / len(currents)
    avg_power = sum(powers) / len(powers)

    voltage_drop = max(voltages) - min(voltages)
    peak_current = max(currents)
    avg_lux = sum(lux_values) / len(lux_values)
    sound_variation = max(sound_values) - min(sound_values)

    status = "PASS"

    if voltage_drop > 1:
        status = "FAIL - Voltage Drop"

    if peak_current > 20:
        status = "FAIL - Overcurrent"

    if sound_variation < 10:
        status = "FAIL - Weak Sound"

    result = {
        "timestamp": str(datetime.now()),
        "avg_voltage": round(avg_voltage,2),
        "avg_current": round(avg_current,2),
        "avg_power": round(avg_power,2),
        "voltage_drop": round(voltage_drop,2),
        "peak_current": round(peak_current,2),
        "avg_lux": round(avg_lux,2),
        "sound_variation": sound_variation,
        "final_status": status
    }

    print("✅ QC RESULT:", result)

    # -------- SEND TO SFS --------
    try:

        response = requests.post(
            "http://127.0.0.1:5001/store_result",
            json=result
        )

        print("📤 Sent to SFS:", response.text)

    except Exception as e:

        print("❌ Failed to send to SFS:", e)

    # -------- SAVE LOCAL CSV --------
    with open(CSV_FILE, 'a', newline='') as f:

        writer = csv.writer(f)

        writer.writerow([
            result["timestamp"],
            result["avg_voltage"],
            result["avg_current"],
            result["avg_power"],
            result["voltage_drop"],
            result["peak_current"],
            result["avg_lux"],
            result["sound_variation"],
            result["final_status"]
        ])

    return result


# -------- GET RESULT --------
@app.route('/get_result')
def get_result():
    return jsonify(last_result)


# -------- MAIN --------
if __name__ == "__main__":

    print("🚗 TSS Server Started")

    app.run(host="0.0.0.0", port=5000)