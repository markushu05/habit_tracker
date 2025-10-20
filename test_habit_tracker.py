# test_habit_tracker.py
import pytest
import os
import sqlite3
from datetime import datetime, timedelta
from habit_manager import HabitManager
from storage import init_db, get_connection
from habit import Habit

TEST_DB = "data/test_habits.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Erstellt eine frische Test-Datenbank für jeden Testlauf."""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            periodicity TEXT CHECK(periodicity IN ('daily','weekly','monthly','yearly')),
            created_at TEXT NOT NULL,
            start_date TEXT,
            due_date TEXT,
            active_days TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)
    conn.commit()
    conn.close()
    yield
    # Cleanup nach Tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def manager(monkeypatch):
    """Fixture für den HabitManager mit Test-Datenbank."""
    # Monkeypatch für Testdatenbank
    from storage import DB_NAME
    monkeypatch.setattr("storage.DB_NAME", TEST_DB)
    return HabitManager()


def test_add_habit(manager):
    """Testet das Erstellen eines Habits."""
    manager.add_habit("Trinken", "daily", ["2025-10-20"])
    habits = manager.get_all_habits()
    assert len(habits) == 1
    assert habits[0].name == "Trinken"
    assert habits[0].periodicity == "daily"


def test_due_date_calculation(manager):
    """Testet, ob die Fälligkeit berechnet wird."""
    manager.add_habit("Laufen", "weekly", ["2025-10-22"])
    habit = manager.get_all_habits()[-1]
    assert habit.due_date is not None
    # Datum ist ein gültiges ISO-Format
    datetime.fromisoformat(habit.due_date)


def test_mark_complete(manager):
    """Testet das Markieren eines Habits als erledigt."""
    manager.add_habit("Lesen", "daily", ["2025-10-20"])
    habit = manager.get_all_habits()[-1]
    manager.mark_habit_complete(habit.id)

    updated = manager.get_habit_by_id(habit.id)
    assert updated.completed == 1


def test_mark_broken(manager):
    """Testet das Markieren eines Habits als gebrochen."""
    manager.add_habit("Sport", "daily", ["2025-10-20"])
    habit = manager.get_all_habits()[-1]
    manager.mark_habit_broken(habit.id)

    updated = manager.get_habit_by_id(habit.id)
    assert updated.completed == 2


def test_streak_calculation(manager):
    """Testet, ob die Streak korrekt berechnet wird."""
    manager.add_habit("Meditieren", "daily", ["2025-10-20"])
    habit = manager.get_all_habits()[-1]

    # Drei Tage in Folge als erledigt markieren
    for i in range(3):
        conn = get_connection()
        conn.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit.id, (datetime.now() - timedelta(days=2 - i)).isoformat())
        )
        conn.commit()
        conn.close()

    streak = manager.get_longest_streak(habit.id)
    assert streak == 3


def test_delete_habit(manager):
    """Testet das Löschen eines Habits."""
    manager.add_habit("Putzen", "weekly", ["2025-10-22"])
    habits_before = manager.get_all_habits()
    habit_id = habits_before[-1].id

    manager.delete_habit(habit_id)
    habits_after = manager.get_all_habits()
    assert len(habits_after) == len(habits_before) - 1
