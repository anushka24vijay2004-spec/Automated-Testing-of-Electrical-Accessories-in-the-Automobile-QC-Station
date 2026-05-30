from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

CSV_FILE = "central_qc_database.csv"

@app.route("/")
def dashboard():

    df = pd.read_csv(CSV_FILE)

    # column spaces remove
    df.columns = df.columns.str.strip()

    timestamps = df["Timestamp"].tolist()
    voltage = df["Avg Voltage"].tolist()
    current = df["Avg Current"].tolist()
    power = df["Avg Power"].tolist()
    lux = df["Avg Lux"].tolist()
    sound = df["Sound Variation"].tolist()
    status = df["Final Status"].tolist()

    total_tests = len(df)
    pass_count = (df["Final Status"] == "PASS").sum()
    fail_count = (df["Final Status"] == "FAIL").sum()

    return render_template(
        "dashboard.html",
        timestamps=timestamps,
        voltage=voltage,
        current=current,
        power=power,
        lux=lux,
        sound=sound,
        status=status,
        total_tests=total_tests,
        pass_count=pass_count,
        fail_count=fail_count
    )


if __name__ == "__main__":
    print("QC Dashboard Running → http://127.0.0.1:5002")
    app.run(host="0.0.0.0", port=5002)