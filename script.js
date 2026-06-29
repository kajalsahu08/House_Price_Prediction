const fields = [
  "longitude",
  "latitude",
  "ocean_proximity",
  "housing_median_age",
  "total_rooms",
  "total_bedrooms",
  "population",
  "households",
  "median_income"
];

// Enter dabane pe next field pe jao
fields.forEach((id, index) => {
  const el = document.getElementById(id);
  el.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const next = fields[index + 1];
      if (next) {
        document.getElementById(next).focus();
      } else {
        // Last field pe Enter = predict
        predict();
      }
    }
  });
});

async function predict() {
  const btn = document.querySelector(".btn");
  btn.textContent = "Predicting...";
  btn.disabled = true;

  document.getElementById("result-card").style.display = "none";
  document.getElementById("error-card").style.display = "none";

  const payload = {
    longitude:          parseFloat(document.getElementById("longitude").value),
    latitude:           parseFloat(document.getElementById("latitude").value),
    housing_median_age: parseFloat(document.getElementById("housing_median_age").value),
    total_rooms:        parseFloat(document.getElementById("total_rooms").value),
    total_bedrooms:     parseFloat(document.getElementById("total_bedrooms").value),
    population:         parseFloat(document.getElementById("population").value),
    households:         parseFloat(document.getElementById("households").value),
    median_income:      parseFloat(document.getElementById("median_income").value),
    ocean_proximity:    parseFloat(document.getElementById("ocean_proximity").value),
  };

  for (const [key, val] of Object.entries(payload)) {
    if (isNaN(val)) {
      showError("Please fill in all fields correctly.");
      reset(btn);
      return;
    }
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (data.success) {
      const formatted = "$" + data.predicted_price.toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      });
      document.getElementById("result-price").textContent = formatted;
      document.getElementById("result-card").style.display = "block";

      // Result card pe scroll karo
      document.getElementById("result-card").scrollIntoView({ behavior: "smooth" });

    } else {
      showError("Prediction failed: " + data.error);
    }
  } catch (err) {
    showError("Could not connect to server. Make sure Flask is running.");
  }

  reset(btn);
}

function showError(msg) {
  document.getElementById("error-msg").textContent = msg;
  document.getElementById("error-card").style.display = "block";
}

function reset(btn) {
  btn.textContent = "🔍 Predict Price";
  btn.disabled = false;
}