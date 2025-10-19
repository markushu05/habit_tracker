# habit.py
import json
from datetime import datetime


class Habit:
    """
    Repräsentiert eine Gewohnheit in der Datenbank.
    """
    def __init__(self, id, name, periodicity, created_at, start_date=None, due_date=None, active_days=None, completed=0):
        self.id = id
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at
        self.start_date = start_date
        self.due_date = due_date
        self.active_days = json.loads(active_days) if isinstance(active_days, str) else active_days
        self.completed = completed

    @classmethod
    def from_row(cls, row):
        """Erzeugt ein Habit-Objekt aus einem DB-Row."""
        return cls(**dict(row))

    def mark_complete(self):
        """Markiert dieses Habit als erledigt."""
        from habit_manager import HabitManager
        HabitManager().mark_habit_complete(self.id)

    def mark_broken(self):
        """Markiert dieses Habit als gebrochen."""
        from habit_manager import HabitManager
        HabitManager().mark_habit_broken(self.id)

    def __repr__(self):
        return f"<Habit {self.id}: {self.name} ({self.periodicity}), status={self.completed}>"
