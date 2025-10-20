# utils.py
from datetime import datetime, timedelta
import calendar

def _to_date_list(active_days):
    """Converts active_days (JSON list or list of strings) to date objects."""
    out = []
    for d in active_days or []:
        if isinstance(d, str):
            try:
                out.append(datetime.strptime(d, "%Y-%m-%d").date())
            except Exception:
                continue
        else:
            out.append(d)  # if already a date
    return sorted(out)

def calculate_next_due_date(habit):
    """
    habit: dict with keys:
      - 'periodicity': 'daily'|'weekly'|'monthly'|'yearly'
      - 'active_days': list of 'YYYY-MM-DD' strings (from calendar), or [].
    Returns ISO date (YYYY-MM-DD) for the next due date (>= today),
    or None if not computable.
    """
    today = datetime.now().date()
    periodicity = (habit.get("periodicity") or "daily")
    active_days = habit.get("active_days") or []

    dates = _to_date_list(active_days)

    # 1) if concrete future dates exist -> return earliest >= today
    future = [d for d in dates if d >= today]
    if future:
        return future[0].isoformat()

    # 2) otherwise: calculate next date based on periodicity
    # if no concrete active_days -> fallback per periodicity
    if not dates:
        if periodicity == "daily":
            return today.isoformat()
        elif periodicity == "weekly":
            return (today + timedelta(days=7 - today.weekday())).isoformat()  # next Sunday-like fallback
        elif periodicity == "monthly":
            day = today.day
            month = today.month + 1 if today.month < 12 else 1
            year = today.year + (1 if month == 1 else 0)
            last_day = calendar.monthrange(year, month)[1]
            day = min(day, last_day)
            return datetime(year, month, day).date().isoformat()
        elif periodicity == "yearly":
            try:
                return datetime(today.year, today.month, today.day).date().isoformat()
            except Exception:
                return datetime(today.year + 1, today.month, today.day).date().isoformat()

    # 3) only past concrete dates exist -> extend last entry periodically until >= today
    last = dates[-1]
    next_date = last

    if periodicity == "daily":
        while next_date < today:
            next_date = next_date + timedelta(days=1)
        return next_date.isoformat()

    if periodicity == "weekly":
        while next_date < today:
            next_date = next_date + timedelta(weeks=1)
        return next_date.isoformat()

    if periodicity == "monthly":
        y, m = last.year, last.month
        day = last.day
        while next_date < today:
            m += 1
            if m > 12:
                m = 1
                y += 1
            last_day = calendar.monthrange(y, m)[1]
            d = min(day, last_day)
            next_date = datetime(y, m, d).date()
        return next_date.isoformat()

    if periodicity == "yearly":
        y = last.year
        month = last.month
        day = last.day
        while next_date < today:
            y += 1
            try:
                next_date = datetime(y, month, day).date()
            except ValueError:
                next_date = datetime(y, month, min(day, 28)).date()
        return next_date.isoformat()

    # fallback
    return today.isoformat()
