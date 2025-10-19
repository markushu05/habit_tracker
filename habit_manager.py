# habit_manager.py
import json
from datetime import datetime
from storage import get_connection
from utils import calculate_next_due_date
from habit import Habit

class HabitManager:
    """Kapselt alle CRUD- und Logikfunktionen für Habits."""

    # --- CRUD ---
    def add_habit(self, name, periodicity, date_list):
        conn = get_connection()
        c = conn.cursor()
        created_at = datetime.now().isoformat()
        selected_dates = json.dumps(date_list)
        habit_dict = {"periodicity": periodicity, "active_days": date_list}
        due_date = calculate_next_due_date(habit_dict)

        c.execute("""
            INSERT INTO habits (name, periodicity, created_at, active_days, due_date, completed)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (name, periodicity, created_at, selected_dates, due_date))
        conn.commit()
        conn.close()

    def update_habit(self, habit_id, name, periodicity, date_list):
        if isinstance(date_list, str):
            date_list = [d.strip() for d in date_list.split(",") if d.strip()]
        elif isinstance(date_list, list) and len(date_list) == 1 and "," in date_list[0]:
            date_list = [d.strip() for d in date_list[0].split(",") if d.strip()]

        conn = get_connection()
        c = conn.cursor()
        selected_dates = json.dumps(date_list)
        habit_dict = {"periodicity": periodicity, "active_days": date_list}
        due_date = calculate_next_due_date(habit_dict)

        c.execute("""
            UPDATE habits SET name = ?, periodicity = ?, active_days = ?, due_date = ?
            WHERE id = ?
        """, (name, periodicity, selected_dates, due_date, habit_id))
        conn.commit()
        conn.close()

    def delete_habit(self, habit_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        c.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.commit()
        conn.close()

    # --- Status ---
    def mark_habit_complete(self, habit_id):
        conn = get_connection()
        c = conn.cursor()
        completed_at = datetime.now().isoformat()

        # Habit aus DB laden
        c.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        habit_row = c.fetchone()
        habit = Habit.from_row(habit_row)

        habit_dict = {"periodicity": habit.periodicity, "active_days": habit.active_days}
        new_due_date = calculate_next_due_date(habit_dict)

        c.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)", (habit_id, completed_at))
        c.execute("UPDATE habits SET completed = 1, due_date = ? WHERE id = ?", (new_due_date, habit_id))
        conn.commit()
        conn.close()

    def mark_habit_broken(self, habit_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE habits SET completed = 2 WHERE id = ?", (habit_id,))
        conn.commit()
        conn.close()

    def update_habit_statuses(self):
        conn = get_connection()
        c = conn.cursor()
        today = datetime.now().date()
        c.execute("SELECT * FROM habits")
        rows = c.fetchall()

        for row in rows:
            habit = Habit.from_row(row)
            if not habit.due_date:
                continue

            due = datetime.fromisoformat(habit.due_date).date()
            if due < today and habit.completed == 0:
                self.mark_habit_broken(habit.id)
            elif due < today and habit.completed == 1:
                habit_dict = {"periodicity": habit.periodicity, "active_days": habit.active_days}
                new_due_date = calculate_next_due_date(habit_dict)
                c.execute("UPDATE habits SET completed = 0, due_date = ? WHERE id = ?", (new_due_date, habit.id))

        conn.commit()
        conn.close()

    # --- Abfragen ---
    def get_all_habits(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM habits")
        habits = [Habit.from_row(row) for row in c.fetchall()]
        conn.close()
        return habits

    def get_habit_by_id(self, habit_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = c.fetchone()
        conn.close()
        return Habit.from_row(row) if row else None

    def get_habits_by_periodicity(self, periodicity):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM habits WHERE periodicity = ?", (periodicity,))
        habits = [Habit.from_row(row) for row in c.fetchall()]
        conn.close()
        return habits

    def get_completions(self, habit_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at", (habit_id,))
        rows = [r["completed_at"] for r in c.fetchall()]
        conn.close()
        return rows

    # --- Streaks ---
    def get_longest_streak(self, habit_id):
        completions = self.get_completions(habit_id)
        if not completions:
            return 0

        dates = [datetime.fromisoformat(c) for c in completions]
        dates.sort()
        habit = self.get_habit_by_id(habit_id)
        period = habit.periodicity

        longest = current = 1
        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i - 1]).days
            if (period == "daily" and diff == 1) or (period == "weekly" and diff <= 7) \
               or (period == "monthly" and diff <= 31) or (period == "yearly" and diff <= 366):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    def get_longest_streak_overall(self):
        habits = self.get_all_habits()
        if not habits:
            return None, 0

        longest_habit = None
        longest_streak = 0

        for h in habits:
            streak = self.get_longest_streak(h.id)
            if streak > longest_streak:
                longest_streak = streak
                longest_habit = h.name
        return longest_habit, longest_streak

    def get_streak(self, habit_id):
        """
        Gibt den aktuellen Streak (aufeinanderfolgende erfolgreiche Perioden bis heute) zurück.
        """
        completions = self.get_completions(habit_id)
        if not completions:
            return 0

        dates = [datetime.fromisoformat(c).date() for c in completions]
        dates.sort()
        habit = self.get_habit_by_id(habit_id)
        period = habit.periodicity
        today = datetime.now().date()

        current_streak = 1
        for i in range(len(dates) - 1, 0, -1):
            diff = (dates[i] - dates[i - 1]).days

            # Prüfe, ob die Abstände zur Periodizität passen
            if (period == "daily" and diff == 1) or \
            (period == "weekly" and diff <= 7) or \
            (period == "monthly" and diff <= 31) or \
            (period == "yearly" and diff <= 366):
                current_streak += 1
            else:
                break

        # Wenn der letzte Completion-Eintrag zu weit zurückliegt, Streak = 0
        last_completion = dates[-1]
        if (period == "daily" and (today - last_completion).days > 1) or \
        (period == "weekly" and (today - last_completion).days > 7) or \
        (period == "monthly" and (today - last_completion).days > 31) or \
        (period == "yearly" and (today - last_completion).days > 366):
            return 0

        return current_streak
