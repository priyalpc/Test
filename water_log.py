# water_tracker.py
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

DB_NAME = "water_intake.db"
DAILY_GOAL = 3000  # 3 liters = 3000 ml

# -------------------------- Database Setup --------------------------
def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS water (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount INTEGER
        )
    """)
    conn.commit()
    conn.close()

# -------------------------- Core Functions --------------------------
def log_water(amount_ml):
    """Logs water in ml for the current day."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Check if entry already exists for today
    c.execute("SELECT amount FROM water WHERE date = ?", (today,))
    row = c.fetchone()

    # Update or Insert
    if row:
        new_amount = row[0] + amount_ml
        c.execute("UPDATE water SET amount = ? WHERE date = ?", (new_amount, today))
    else:
        c.execute("INSERT INTO water (date, amount) VALUES (?, ?)", (today, amount_ml))

    conn.commit()
    conn.close()

    return new_amount if row else amount_ml


def get_today_progress():
    """Returns today's water intake."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT amount FROM water WHERE date = ?", (today,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def get_last_7_days():
    """Fetch last 7 days of data."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    start_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
    c.execute("""
        SELECT date, amount FROM water
        WHERE date >= ?
        ORDER BY date
    """, (start_date,))
    rows = c.fetchall()
    conn.close()
    return rows


# -------------------------- Plot Chart --------------------------
def plot_weekly_hydration():
    data = get_last_7_days()

    if not data:
        print("No hydration data for the last 7 days.")
        return

    dates = [d for d, _ in data]
    amounts = [a for _, a in data]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, amounts, marker='o')
    plt.axhline(DAILY_GOAL, color='r', linestyle='--', label="Daily Goal (3000 ml)")
    plt.title("Weekly Hydration Chart")
    plt.ylabel("Water Intake (ml)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


# -------------------------- Main Menu --------------------------
def main():
    create_table()

    while True:
        print("\n====== WATER INTAKE TRACKER ======")
        print("1. Log water intake")
        print("2. Show today's progress")
        print("3. Show weekly hydration chart")
        print("4. Exit")

        choice = input("\nSelect an option (1–4): ")

        if choice == "1":
            try:
                amount = int(input("Enter water amount (ml): "))
                total = log_water(amount)
                progress = (total / DAILY_GOAL) * 100
                print(f"\nAdded {amount} ml! Today's total: {total} ml ({progress:.1f}% of goal).")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "2":
            total = get_today_progress()
            progress = (total / DAILY_GOAL) * 100
            print(f"\nToday's intake: {total} ml ({progress:.1f}% of 3L goal).")

        elif choice == "3":
            plot_weekly_hydration()

        elif choice == "4":
            print("Goodbye! Stay hydrated 💧")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
