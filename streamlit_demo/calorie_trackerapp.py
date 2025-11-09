import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Smart Calorie Tracker", page_icon="🥗", layout="centered")

st.title("🥗 Smart Calorie & Macro Tracker")
st.write("Track your meals with automatic calorie estimation based on ingredients and measurements!")

# --- Mock Ingredient Calorie Database (per unit) ---
# These are average estimates (you can expand or connect to an API like Edamam or Nutritionix)
FOOD_DB = {
    "Chicken Breast": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "Rice (cooked)": {"cal": 206, "protein": 4.3, "carbs": 45, "fat": 0.4},
    "Egg": {"cal": 78, "protein": 6, "carbs": 0.6, "fat": 5},
    "Oats": {"cal": 150, "protein": 5, "carbs": 27, "fat": 3},
    "Milk": {"cal": 103, "protein": 8, "carbs": 12, "fat": 2.4},
    "Apple": {"cal": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
    "Banana": {"cal": 105, "protein": 1.3, "carbs": 27, "fat": 0.3},
    "Broccoli": {"cal": 55, "protein": 4.7, "carbs": 11, "fat": 0.6},
    "Olive Oil": {"cal": 119, "protein": 0, "carbs": 0, "fat": 13.5},
    "Peanut Butter": {"cal": 188, "protein": 8, "carbs": 6, "fat": 16},
}

MEASURE_CONVERSION = {
    "cup": 1,
    "tablespoon": 0.0625,
    "teaspoon": 0.0208,
    "piece": 1
}

# --- Initialize session state ---
if "entries" not in st.session_state:
    st.session_state.entries = []

# --- Sidebar: Daily Goals ---
st.sidebar.header("🎯 Daily Nutrition Goals")
daily_cal_goal = st.sidebar.number_input("Daily Calorie Goal (kcal)", min_value=100, value=2000, step=50)
protein_goal = st.sidebar.number_input("Protein Goal (g)", min_value=0, value=120, step=5)
carbs_goal = st.sidebar.number_input("Carbs Goal (g)", min_value=0, value=200, step=5)
fats_goal = st.sidebar.number_input("Fats Goal (g)", min_value=0, value=70, step=5)

# --- Meal Input ---
st.header("🍽️ Add a Meal")

meal_category = st.selectbox("Meal Category", ["Breakfast", "Lunch", "Dinner"])
ingredient = st.selectbox("Select Ingredient", list(FOOD_DB.keys()))
quantity = st.number_input("Quantity", min_value=0.0, step=0.5)
measure = st.selectbox("Measurement", list(MEASURE_CONVERSION.keys()))
date = st.date_input("Date", datetime.now())

if st.button("➕ Add Ingredient"):
    if quantity > 0:
        conv_factor = MEASURE_CONVERSION[measure]
        cal_data = FOOD_DB[ingredient]
        calories = round(cal_data["cal"] * quantity * conv_factor, 1)
        protein = round(cal_data["protein"] * quantity * conv_factor, 1)
        carbs = round(cal_data["carbs"] * quantity * conv_factor, 1)
        fat = round(cal_data["fat"] * quantity * conv_factor, 1)

        entry = {
            "Date": date,
            "Meal Type": meal_category,
            "Ingredient": ingredient,
            "Quantity": f"{quantity} {measure}",
            "Calories": calories,
            "Protein (g)": protein,
            "Carbs (g)": carbs,
            "Fats (g)": fat,
        }

        st.session_state.entries.append(entry)
        st.success(f"✅ Added {ingredient} ({calories} kcal)")
    else:
        st.warning("Please enter a valid quantity.")

# --- Display Meal Log ---
if st.session_state.entries:
    st.header("📊 Meal Log")
    df = pd.DataFrame(st.session_state.entries)
    st.dataframe(df, use_container_width=True)

    # --- Summary ---
    total_cal = df["Calories"].sum()
    total_protein = df["Protein (g)"].sum()
    total_carbs = df["Carbs (g)"].sum()
    total_fats = df["Fats (g)"].sum()

    st.subheader("📈 Daily Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{total_cal:.1f} kcal", f"{total_cal - daily_cal_goal:.1f} from goal")
    col2.metric("Protein", f"{total_protein:.1f} g", f"{total_protein - protein_goal:.1f} from goal")
    col3.metric("Carbs", f"{total_carbs:.1f} g", f"{total_carbs - carbs_goal:.1f} from goal")
    col4.metric("Fats", f"{total_fats:.1f} g", f"{total_fats - fats_goal:.1f} from goal")

    # --- Breakdown by Meal ---
    st.subheader("🍴 Meal Type Breakdown")
    meal_summary = df.groupby("Meal Type")[["Calories", "Protein (g)", "Carbs (g)", "Fats (g)"]].sum()
    st.bar_chart(meal_summary)

    if st.button("🗑️ Clear All Entries"):
        st.session_state.entries = []
        st.warning("All entries cleared!")
else:
    st.info("No meal entries yet. Add ingredients above to get started!")

# --- Footer ---
st.markdown("---")
st.caption("Health is wealth")
