from datetime import date, timedelta
from typing import Union


class Day:
    def __init__(self, value: Union[date, 'Day']):
        if isinstance(value, Day):
            self._date = value._date
        else:
            self._date = value
    
    @classmethod
    def today(cls) -> 'Day':
        return cls(date.today())
    
    @property
    def date(self) -> date:
        return self._date
    
    def next_day(self) -> 'Day':
        return Day(self._date + timedelta(days=1))
    
    def previous_day(self) -> 'Day':
        return Day(self._date - timedelta(days=1))
    
    def add_days(self, days: int) -> 'Day':
        return Day(self._date + timedelta(days=days))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Day):
            return False
        return self._date == other._date
    
    def __str__(self) -> str:
        return self._date.strftime("%d.%m.%Y")
    
    def __repr__(self) -> str:
        return f"Day({self._date})"