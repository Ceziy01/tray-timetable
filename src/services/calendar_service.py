import json
import requests
from icalendar import Calendar as iCalendar
from datetime import datetime
from typing import List, Tuple
from pathlib import Path
from dateutil.rrule import rrulestr

from src.models.day import Day
from src.utils.constants import CACHE_DIR

class CalendarService:
    def __init__(self):
        self.calendar = None
        self.group = None
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
    
    def load_calendar(self, group: str) -> None:
        self.group = group
        self.calendar = self._get_calendar(group)
    
    def _get_calendar(self, group: str) -> iCalendar:
        cal = None
        try:
            session = requests.Session()
            response = session.get(f"https://schedule-of.mirea.ru/schedule/api/search?limit=15&match={group}")
            url = json.loads(response.text)["data"][0]["iCalLink"]
            response = session.get(url)
            data = response.content
            cal = iCalendar.from_ical(data)
    
            cache_file = self.cache_dir / f"{group}.ics"
            with open(cache_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except:
            try:
                cache_file = self.cache_dir / f"{group}.ics"
                with open(cache_file, "rb") as f:
                    cal = iCalendar.from_ical(f.read())
            except:
                raise Exception("Не удалось загрузить расписание")
        return cal
    
    def get_events_for_day(self, day: Day) -> List[Tuple]:
        events_today = []
        target_date = day.date
        
        for component in self.calendar.walk():
            if component.name != "VEVENT":
                continue
            
            dtstart = component.get('DTSTART').dt
            dtend = component.get("DTEND").dt
            summary = component.get('SUMMARY')
            rrule = component.get('RRULE')
            exdate = component.get('EXDATE')
            location = component.get('LOCATION')

            exdates = []
            occurrences = []
            
            if exdate:
                if isinstance(exdate, list):
                    for ex in exdate:
                        if hasattr(ex, 'dts'):
                            exdates.extend([dt.dt for dt in ex.dts])
                else:
                    if hasattr(exdate, 'dts'):
                        exdates = [dt.dt for dt in exdate.dts]

            if rrule:
                until = rrule.get("UNTIL")[0] if rrule.get("UNTIL") else None
                rrule_str = rrule.to_ical().decode()
                rule = rrulestr(rrule_str, dtstart=dtstart)
                if dtend and until:
                    try:
                        occurrences = [d.date() for d in rule if d < until and d not in exdates]
                    except:
                        occurrences = []

            event_time = None
            if isinstance(dtstart, datetime):
                event_time = dtstart.time().strftime("%H:%M")

            dtstart_date = dtstart.date() if isinstance(dtstart, datetime) else dtstart
            dtend_date = dtend.date() if isinstance(dtend, datetime) else dtend

            if ((dtstart_date <= target_date <= dtend_date) or (target_date in occurrences)):
                events_today.append((str(summary), event_time, str(location) if location else None))
        
        return events_today