from flask import Flask, request, jsonify
from datetime import datetime
import json
import csv
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
SAMPLE_LIMIT = 5
capture_mode = False
capture_buffer = []
last_result = None
CSV_FILE = "qc_report.csv"

# ---------------- CREATE CSV IF NOT EXISTS ----------------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp",
            "Avg Voltage (V)",
            "Avg Current (mA)",
            "Avg Power (mW)",
            "Voltage Drop (V)",
            "Peak Current (mA)",
            "Avg Lux",
            "Sound Variation",
            "Final Status"
        ])

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "🚗 TSS QC Server Running (Controlled Mode)"

# ---------------- START CAPTURE ----------------
@app.route('/start_capture', methods=['POST'])
def start_capture():
    global capture_mode, capture_buffer
    capture_mode = True
    capture_buffer = []
    print("\n🔒 Capture Mode Activated...\n")
    return jsonify({"status": "capture_started"}), 200

# ---------------- RECEIVE DATA ----------------
@app.route('/data', methods=['POST'])
def receive_data():
    global capture_mode, capture_buffer, last_result

    try:
        data = request.get_json()

        # Save latest packet for monitoring
        with open("latest_data.json", "w") as f:
            json.dump(data, f)

        if capture_mode:
            capture_buffer.append(data)
            print(f"📥 Capturing Sample {len(capture_buffer)}/{SAMPLE_LIMIT}")

            if len(capture_buffer) >= SAMPLE_LIMIT:
                last_result = analyze_data(capture_buffer)
                capture_mode = False
                capture_buffer = []

                return jsonify({
                    "status": "captured",
                    "analysis": last_result
                }), 200

        return jsonify({"status": "collecting"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"}), 400


# ---------------- ANALYSIS ENGINE ----------------
def analyze_data(buffer):

    voltages = [d.get("voltage", 0) for d in buffer]
    currents = [d.get("current", 0) for d in buffer]
    powers = [d.get("power", 0) for d in buffer]
    lux_values = [d.get("lux", 0) for d in buffer]
    sound_values = [d.get("sound", 0) for d in buffer]

    avg_voltage = sum(voltages) / len(voltages)
    avg_current = sum(currents) / len(currents)
    avg_power = sum(powers) / len(powers)

    voltage_drop = max(voltages) - min(voltages)
    peak_current = max(currents)
    avg_lux = sum(lux_values) / len(lux_values)
    sound_variation = max(sound_values) - min(sound_values)

    # -------- DECISION LOGIC --------
    status = "PASS"

    # Voltage Check
    if voltage_drop > 1.5:
        status = "FAIL - High Voltage Drop"
    elif voltage_drop > 0.8:
        status = "WARNING - Moderate Voltage Drop"

    # Current Check (mA scale)
    if peak_current > 20:
        status = "FAIL - Overcurrent"
    elif peak_current > 10 and "FAIL" not in status:
        status = "WARNING - High Current"

    # Sound Check (Adjusted for Prototype)
    if sound_variation < 10:
        status = "FAIL - Weak Sound"
    elif sound_variation < 20 and "FAIL" not in status:
        status = "WARNING - Low Sound"

    analysis_result = {
        "avg_voltage": round(avg_voltage, 2),
        "avg_current": round(avg_current, 2),
        "avg_power": round(avg_power, 2),
        "voltage_drop": round(voltage_drop, 2),
        "peak_current": round(peak_current, 2),
        "avg_lux": round(avg_lux, 2),
        "sound_variation": sound_variation,
        "final_status": status
    }

    print("\n===== QC LOCKED RESULT =====")
    for key, value in analysis_result.items():
        print(f"{key} : {value}")
    print("=============================\n")

    # Save to CSV
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            avg_voltage,
            avg_current,
            avg_power,
            voltage_drop,
            peak_current,
            avg_lux,
            sound_variation,
            status
        ])

    return analysis_result


# ---------------- GET LAST RESULT ----------------
@app.route('/get_result', methods=['GET'])
def get_result():
    return jsonify(last_result)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🚗 TSS QC Server Running (Industrial Controlled Locking)...")
    app.run(host="0.0.0.0", port=5000)