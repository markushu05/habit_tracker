# habit.py
import json
from datetime import datetime


class Habit:
    """
    Represents a habit in the database.
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
        """Creates a Habit object from a database row."""
        return cls(**dict(row))

    def mark_complete(self):
        """Marks this habit as completed."""
        from habit_manager import HabitManager
        HabitManager().mark_habit_complete(self.id)

    def mark_broken(self):
        """Marks this habit as broken."""
        from habit_manager import HabitManager
        HabitManager().mark_habit_broken(self.id)

    def __repr__(self):
        return f"<Habit {self.id}: {self.name} ({self.periodicity}), status={self.completed}>"
