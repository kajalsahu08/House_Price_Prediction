import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# 1. LOAD DATA
# ──────────────────────────────────────────────
df = pd.read_csv("housing.csv")
print("Shape:", df.shape)
print(df.head())

# ──────────────────────────────────────────────
# 2. DATA PREPROCESSING
# ──────────────────────────────────────────────

# Fill missing values (total_bedrooms has some nulls)
df["total_bedrooms"].fillna(df["total_bedrooms"].median(), inplace=True)

# Encode categorical column
le = LabelEncoder()
df["ocean_proximity"] = le.fit_transform(df["ocean_proximity"])

# ──────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ──────────────────────────────────────────────

df["rooms_per_household"]    = df["total_rooms"]    / df["households"]
df["bedrooms_per_room"]      = df["total_bedrooms"] / df["total_rooms"]
df["population_per_household"] = df["population"]   / df["households"]

# ──────────────────────────────────────────────
# 4. SPLIT FEATURES & TARGET
# ──────────────────────────────────────────────

X = df.drop("median_house_value", axis=1)
y = df["median_house_value"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ──────────────────────────────────────────────
# 5. SCALE FEATURES
# ──────────────────────────────────────────────

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ──────────────────────────────────────────────
# 6. MODEL COMPARISON + CROSS VALIDATION
# ──────────────────────────────────────────────

models = {
    "Linear Regression":       LinearRegression(),
    "Random Forest":           RandomForestRegressor(n_estimators=100, random_state=42),
    "Gradient Boosting":       GradientBoostingRegressor(n_estimators=100, random_state=42),
    "XGBoost":                 XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
}

kf = KFold(n_splits=5, shuffle=True, random_state=42)
results = []

print("\n── Model Comparison (5-Fold Cross Validation) ──\n")

for name, model in models.items():
    cv_scores = cross_val_score(model, X_train_scaled, y_train,
                                cv=kf, scoring="r2")
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)
    cv_mean = cv_scores.mean()

    results.append({
        "Model": name,
        "MAE":   round(mae, 2),
        "RMSE":  round(rmse, 2),
        "R2":    round(r2, 4),
        "CV R2": round(cv_mean, 4)
    })

    print(f"{name}")
    print(f"  MAE:  {mae:,.0f}  |  RMSE: {rmse:,.0f}  |  R²: {r2:.4f}  |  CV R²: {cv_mean:.4f}\n")

results_df = pd.DataFrame(results)
print(results_df.sort_values("R2", ascending=False))

# ──────────────────────────────────────────────
# 7. SAVE BEST MODEL (XGBoost usually wins)
# ──────────────────────────────────────────────

best_model = models["XGBoost"]
joblib.dump(best_model, "model.pkl")
joblib.dump(scaler,     "scaler.pkl")
joblib.dump(list(X.columns), "features.pkl")

print("\n✅ model.pkl, scaler.pkl, features.pkl saved!")