# gym_logger_streamlit.py
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import altair as alt

DB_NAME = "workout_log.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_workout(exercise, sets, reps, weight, date=None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO workouts (date, exercise, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
              (date, exercise, int(sets), int(reps), float(weight)))
    conn.commit()
    conn.close()

@st.cache_data
def load_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM workouts ORDER BY date DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df

# ---- Streamlit layout ----
st.set_page_config(page_title="Gym Logger", layout="centered")
create_table()

st.header("🏋️ Gym Workout Logger")

# Responsive columns: on narrow screens these stack
col1, col2 = st.columns([2,1])

with col1:
    with st.form("log_form", clear_on_submit=True):
        ex = st.text_input("Exercise (e.g. Bench Press)")
        sets = st.number_input("Sets", min_value=1, max_value=20, value=3, step=1)
        reps = st.number_input("Reps", min_value=1, max_value=100, value=8, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=20.0, step=0.5, format="%.1f")
        submitted = st.form_submit_button("Add Workout")
        if submitted:
            if not ex.strip():
                st.warning("Please enter an exercise name.")
            else:
                insert_workout(ex.strip(), sets, reps, weight)
                st.success("Logged workout.")
                st.experimental_rerun()

with col2:
    st.markdown("**Quick Stats**")
    df = load_df()
    total_entries = 0 if df.empty else len(df)
    st.metric("Total entries", total_entries)
    if not df.empty:
        last = df.iloc[0]
        st.write(f"Last: **{last['exercise']}** on {last['date']} — {int(last['sets'])}x{int(last['reps'])} @ {last['weight']}kg")

st.markdown("---")

# Filters and view
df = load_df()
exercises = sorted(df['exercise'].unique().tolist()) if not df.empty else []
filter_cols = st.columns([2,1,1])

with filter_cols[0]:
    sel_ex = st.selectbox("Filter exercise", options=["All"] + exercises)
with filter_cols[1]:
    days = st.selectbox("Time range", options=[7, 30, 90, 365, "All"], index=0)
with filter_cols[2]:
    show_table = st.checkbox("Show table", value=True)

# Apply filters
if not df.empty:
    filtered = df.copy()
    if sel_ex and sel_ex != "All":
        filtered = filtered[filtered['exercise'] == sel_ex]
    if days != "All":
        cutoff = datetime.now().date() - timedelta(days=int(days))
        filtered = filtered[pd.to_datetime(filtered['date']).dt.date >= cutoff]
else:
    filtered = df

if show_table:
    st.subheader("Entries")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# Charts
st.subheader("Progress Charts")
chart_cols = st.columns(2)

# Chart function
def plot_progress(df_chart, title):
    if df_chart.empty:
        st.write("No data to plot.")
        return
    # prepare daily max weight (could be average or max)
    df_chart['date'] = pd.to_datetime(df_chart['date']).dt.date
    daily = df_chart.groupby('date')['weight'].max().reset_index()
    chart = alt.Chart(daily).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('weight:Q', title='Weight (kg)'),
        tooltip=['date', 'weight']
    ).properties(width='container', height=300, title=title)
    st.altair_chart(chart, use_container_width=True)

with chart_cols[0]:
    st.markdown("**Weekly**")
    if sel_ex == "All":
        df_week = df.copy()
    else:
        df_week = df[df['exercise'] == sel_ex]
    if not df_week.empty:
        cutoff = datetime.now().date() - timedelta(days=7)
        df_week = df_week[pd.to_datetime(df_week['date']).dt.date >= cutoff]
    plot_progress(df_week, f"Last 7 days — {sel_ex}")

with chart_cols[1]:
    st.markdown("**Monthly**")
    if sel_ex == "All":
        df_month = df.copy()
    else:
        df_month = df[df['exercise'] == sel_ex]
    if not df_month.empty and days != "All":
        cutoff = datetime.now().date() - timedelta(days=30)
        df_month = df_month[pd.to_datetime(df_month['date']).dt.date >= cutoff]
    plot_progress(df_month, f"Last 30 days — {sel_ex}")

st.markdown("---")
st.caption("Works offline using local SQLite DB (workout_log.db). On Streamlit Cloud, the app will be ephemeral unless you mount persistent storage.")
