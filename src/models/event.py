from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any


@dataclass
class CalendarEvent:
    summary: str
    start_time: Optional[Any]
    end_time: Optional[Any]
    location: Optional[str]
    event_type: str
    time_str: Optional[str] = None
    
    @property
    def pair_name(self) -> str:
        parts = self.summary.split()
        if len(parts) > 1:
            return " ".join(parts[1:])
        return self.summary
    
    @property
    def pair_type_code(self) -> str:
        return self.summary.split()[0] if self.summary else ""
    
    @property
    def date_only(self) -> Optional[date]:
        if isinstance(self.start_time, datetime):
            return self.start_time.date()
        return self.start_time if isinstance(self.start_time, date) else None
    
    def __hash__(self):
        return hash((self.summary, self.time_str, self.location))
    
    def __eq__(self, other):
        if not isinstance(other, CalendarEvent):
            return False
        return (self.summary == other.summary and 
                self.time_str == other.time_str and 
                self.location == other.location)