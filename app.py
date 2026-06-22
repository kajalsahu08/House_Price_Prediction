from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np

app = Flask(__name__)

model    = joblib.load("model.pkl")
scaler   = joblib.load("scaler.pkl")
features = joblib.load("features.pkl")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        longitude  = float(data["longitude"])
        latitude   = float(data["latitude"])
        age        = float(data["housing_median_age"])
        rooms      = float(data["total_rooms"])
        bedrooms   = float(data["total_bedrooms"])
        population = float(data["population"])
        households = float(data["households"])
        income     = float(data["median_income"])
        ocean      = float(data["ocean_proximity"])

        # Feature engineering (must match train_model.py)
        rooms_per_hh   = rooms    / households
        bedrooms_ratio = bedrooms / rooms
        pop_per_hh     = population / households

        input_data = np.array([[
            longitude, latitude, age, rooms, bedrooms,
            population, households, income, ocean,
            rooms_per_hh, bedrooms_ratio, pop_per_hh
        ]])

        scaled     = scaler.transform(input_data)
        prediction = model.predict(scaled)[0]

        return jsonify({
            "success": True,
            "predicted_price": round(float(prediction), 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)