import sys
import psutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

from src.ui.tray_icon import TrayIcon
from src.models.day import Day
from src.services.calendar_service import CalendarService
from src.services.icon_service import IconService
from src.utils.constants import DEFAULT_GROUP, ICON_PATH, PROCESS_NAME


def is_already_running() -> bool:
    running_processes = [proc.name() for proc in psutil.process_iter()]
    return running_processes.count(PROCESS_NAME) > 1


def main():
    if is_already_running():
        print("Application already running, exiting...")
        sys.exit()

    app = QApplication(sys.argv)

    palette = app.palette()
    accent_color = palette.color(QPalette.ColorRole.Accent)
    icon = IconService.colorize_icon(ICON_PATH, accent_color)
    calendar_service = CalendarService()
    current_day = Day.today()

    try:
        print(f"Loading calendar for group: {DEFAULT_GROUP}")
        calendar_service.load_calendar(DEFAULT_GROUP)
        events = calendar_service.get_events_for_day(current_day)
        print(f"Found {len(events)} events for today")
        for event in events:
            print(f"  - {event.summary} at {event.time_str}")
            
    except Exception as e:
        print(f"Error loading calendar: {e}")
    
    tray_icon = TrayIcon(icon, calendar_service, current_day, DEFAULT_GROUP)
    tray_icon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()