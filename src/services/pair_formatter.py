from typing import List, Tuple
from datetime import date

from src.utils.constants import PAIR_TYPE_STYLES, PAIR_SHORT_NAMES
from src.utils.date_utils import get_weekday_name

class PairFormatter:
    @staticmethod
    def remove_duplicates(arr: List[Tuple]) -> List[Tuple]:
        result = []
        for item in arr:
            if item not in result:
                result.append(item)
        return result
    
    @staticmethod
    def get_short_pair_name(name: str) -> str:
        if name in PAIR_SHORT_NAMES:
            return PAIR_SHORT_NAMES[name]
        return name
    
    @staticmethod
    def get_pair_type_html(type_code: str) -> str:
        if type_code in PAIR_TYPE_STYLES:
            return PAIR_TYPE_STYLES[type_code]
        return type_code
    
    @staticmethod
    def format_events(day: date, events: List[Tuple], group: str) -> str:
        text = ""
        title = ""
        w = 0
  
        processed_events = []
        for summary, time_, location in events:
            if summary:
                
                parts = summary.split()
                if len(parts) > 1:
                    t = " ".join(parts[1:])
                    shortened_name = PairFormatter.get_short_pair_name(t)
                    summary = summary.replace(t, shortened_name)
            processed_events.append((summary, time_, location))
 
        unique_events = PairFormatter.remove_duplicates(processed_events)
 
        for summary, time_, location in unique_events:
            if location:
                location = location.replace(" (МП-1)", "").replace(" (В-78)", "")
            if time_:
                parts = summary.split()
                if parts:
                    t = parts[0]
                    name = summary[len(t):] if len(parts) > 1 else ""
                    pair = f"<b>&bull; {time_}</b> - <i>{name}</i>"                    
                    if location and location not in ["кафедра", "Дистанционно (СДО)"]:
                        pair += f" <span style=\"color:gray;\">({location})</span>"
                    pair += f" &nbsp;{PairFormatter.get_pair_type_html(t)}<br>"
                    text += pair
            else:
                if "неделя" in summary:
                    try:
                        week_num = int(summary.split()[0])
                        w = max(week_num, w)
                    except:
                        pass
                if summary == "Сессия":
                    title += " Cессия"

        week_str = f"{w} неделя{title}" if w != 0 else ""
        day_str = day.strftime('%d.%m')
        weekday_str = get_weekday_name(day.weekday())
        
        header = f"<b>{week_str} ({day_str} {weekday_str})  {group}</b><br><br>"

        if not text:
            text = "Пар в этот день нет! :)    "
        
        result = header + text
        if result.endswith("<br>"):
            result = result[:-4]
        
        return result