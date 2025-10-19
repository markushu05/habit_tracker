# utils.py
from datetime import datetime, timedelta
import json

def calculate_next_due_date(habit):
    """
    Berechnet das nächste Fälligkeitsdatum basierend auf Periodizität und aktivierten Tagen.
    habit: dict mit keys 'periodicity' (daily, weekly, monthly, yearly) und 'active_days' (Liste von Datumsstrings)
    """
    today = datetime.now().date()
    periodicity = habit.get("periodicity", "daily")
    active_days = habit.get("active_days", [])

    # Wenn keine aktiven Tage angegeben, Fälligkeit auf heute setzen
    if not active_days:
        return today.isoformat()

    # Konvertiere Strings in date-Objekte
    dates = []
    for d in active_days:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d").date()
            dates.append(dt)
        except ValueError:
            continue

    # sortiere aufsteigend
    dates.sort()

    if periodicity == "daily":
        # bei daily: nächster Tag nach heute, mindestens heute
        next_due = max(today, dates[0])
        return next_due.isoformat()

    elif periodicity == "weekly":
        # nächste Woche auswählen, gleiche Wochentage wie in active_days
        weekdays = [d.weekday() for d in dates]  # 0=Mo,6=So
        today_weekday = today.weekday()
        # nächster passender Wochentag
        for i in range(7):
            candidate = today + timedelta(days=i)
            if candidate.weekday() in weekdays:
                return candidate.isoformat()
        # fallback
        return (today + timedelta(days=7)).isoformat()

    elif periodicity == "monthly":
        # nimm den nächsten Tag im Monat aus active_days oder gleichen Tag nächsten Monat
        day_nums = [d.day for d in dates]
        today_day = today.day
        next_days = [day for day in day_nums if day >= today_day]
        if next_days:
            next_due = today.replace(day=next_days[0])
        else:
            # nächsten Monat
            month = today.month + 1 if today.month < 12 else 1
            year = today.year + 1 if month == 1 else today.year
            day = day_nums[0]
            # prüfen, ob Tag im Monat existiert
            try:
                next_due = datetime(year, month, day).date()
            except ValueError:
                # falls Tag zu groß für Monat, nimm letzten Tag im Monat
                from calendar import monthrange
                last_day = monthrange(year, month)[1]
                next_due = datetime(year, month, last_day).date()
        return next_due.isoformat()

    elif periodicity == "yearly":
        # nächster Fälligkeitstag im Jahr
        month_days = [(d.month, d.day) for d in dates]
        for month, day in month_days:
            try:
                candidate = datetime(today.year, month, day).date()
            except ValueError:
                continue
            if candidate >= today:
                return candidate.isoformat()
        # nächstes Jahr
        month, day = month_days[0]
        return datetime(today.year + 1, month, day).date().isoformat()

    # fallback
    return today.isoformat()
