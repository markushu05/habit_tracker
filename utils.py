# utils.py
from datetime import datetime, timedelta
import calendar

def _to_date_list(active_days):
    """Konvertiert active_days (JSON-Liste oder Liste von Strings) zu date-Objekten."""
    out = []
    for d in active_days or []:
        if isinstance(d, str):
            try:
                out.append(datetime.strptime(d, "%Y-%m-%d").date())
            except Exception:
                continue
        else:
            out.append(d)  # falls schon date
    return sorted(out)

def calculate_next_due_date(habit):
    """
    habit: dict mit keys:
      - 'periodicity': 'daily'|'weekly'|'monthly'|'yearly'
      - 'active_days': Liste von 'YYYY-MM-DD' strings (aus dem Kalender), oder [].
    Liefert ISO-Datum (YYYY-MM-DD) für das nächste Fälligkeitsdatum (>= heute),
    oder None, falls nicht berechenbar.
    """
    today = datetime.now().date()
    periodicity = (habit.get("periodicity") or "daily")
    active_days = habit.get("active_days") or []

    dates = _to_date_list(active_days)

    # 1) wenn konkrete future-dates vorhanden -> das früheste ≥ today zurückgeben
    future = [d for d in dates if d >= today]
    if future:
        return future[0].isoformat()

    # 2) sonst: baue das nächste Datum basierend auf Periodizität
    # wenn keine konkreten active_days vorhanden -> fallback je Periodizität
    if not dates:
        # kein konkreter Tag gewählt -> use periodicity defaults
        if periodicity == "daily":
            return today.isoformat()
        elif periodicity == "weekly":
            return (today + timedelta(days=7 - today.weekday())).isoformat()  # nächster Sonntag-ähnlich fallback
        elif periodicity == "monthly":
            # nächster Monat, gleicher Tag (oder letzter Tag, falls nicht vorhanden)
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

    # 3) es gibt nur vergangene konkrete dates -> erweitere den letzten Eintrag periodisch,
    # bis ein Datum >= today entsteht
    last = dates[-1]
    next_date = last

    if periodicity == "daily":
        # nächster Tag nach last, wiederholend bis >= today
        while next_date < today:
            next_date = next_date + timedelta(days=1)
        return next_date.isoformat()

    if periodicity == "weekly":
        # add 7 days wiederholt
        while next_date < today:
            next_date = next_date + timedelta(weeks=1)
        return next_date.isoformat()

    if periodicity == "monthly":
        # add months until >= today
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
                # fallback, falls 29. Feb etc.
                next_date = datetime(y, month, min(day, 28)).date()
        return next_date.isoformat()

    # fallback
    return today.isoformat()
