from flask import Flask, render_template, request, redirect, url_for
import json
from habit_manager import HabitManager

app = Flask(__name__)
manager = HabitManager()  # Ein Manager für alle Operationen

@app.route("/")
def index():
    # überprüft beim Aufruf der Startseite, ob Habits gebrochen oder Zyklus erneuert werden müssen
    manager.update_habit_statuses()
    habits = manager.get_all_habits()
    for h in habits:
        h.current_streak = manager.get_streak(h.id)
    return render_template("index.html", habits=habits)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        periodicity = request.form["periodicity"]
        selected_dates = request.form["selected_dates"]

        date_list = [d.strip() for d in selected_dates.split(",") if d.strip()]
        manager.add_habit(name, periodicity, date_list)
        return redirect(url_for("index"))

    return render_template("create.html")

@app.route("/complete/<int:habit_id>")
def complete(habit_id):
    habit = manager.get_habit_by_id(habit_id)
    if habit:
        habit.mark_complete()
    return redirect(url_for("index"))

@app.route("/uncomplete/<int:habit_id>")
def uncomplete(habit_id):
    habit = manager.get_habit_by_id(habit_id)
    if habit:
        habit.mark_broken()
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>")
def delete_habit_route(habit_id):
    manager.delete_habit(habit_id)
    return redirect(url_for("index"))

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    habit = manager.get_habit_by_id(habit_id)
    if habit is None:
        return "Habit nicht gefunden", 404

    if request.method == "POST":
        name = request.form["name"]
        periodicity = request.form["periodicity"]
        date_list = request.form.getlist("dates[]")
        manager.update_habit(habit_id, name, periodicity, date_list)
        return redirect(url_for("habit_detail", habit_id=habit_id))

    selected_dates = habit.active_days if habit.active_days else []
    return render_template("edit.html", habit=habit, selected_dates=selected_dates)

@app.route("/habit/<int:habit_id>")
def habit_detail(habit_id):
    habit = manager.get_habit_by_id(habit_id)
    if not habit:
        return "Habit nicht gefunden", 404

    selected_dates = habit.active_days if habit.active_days else []
    completions = manager.get_completions(habit_id)
    return render_template("detail.html", habit=habit, selected_dates=selected_dates, completions=completions)

@app.route("/analysis")
def analysis():
    habits = manager.get_all_habits()
    daily_habits = manager.get_habits_by_periodicity("daily")
    weekly_habits = manager.get_habits_by_periodicity("weekly")
    monthly_habits = manager.get_habits_by_periodicity("monthly")
    yearly_habits = manager.get_habits_by_periodicity("yearly")
    longest_habit, longest_streak = manager.get_longest_streak_overall()

    return render_template(
        "analysis.html",
        habits=habits,
        daily_habits=daily_habits,
        weekly_habits=weekly_habits,
        monthly_habits=monthly_habits,
        yearly_habits=yearly_habits,
        longest_habit=longest_habit,
        longest_streak=longest_streak
    )

if __name__ == "__main__":
    from storage import init_db
    init_db()
    manager.update_habit_statuses()
    app.run(debug=True)
