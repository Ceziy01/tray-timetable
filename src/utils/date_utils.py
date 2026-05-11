def get_weekday_name(n: int) -> str:
    """Exactly like original getWeekDay"""
    try:
        return ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][n]
    except:
        return ""