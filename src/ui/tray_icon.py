from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtCore import QTimer

# Импортируем оригинальный TrayTooltip
from src.ui.TrayToolTip import TrayTooltip
from src.models.day import Day
from src.services.calendar_service import CalendarService
from src.services.pair_formatter import PairFormatter


class TrayIcon(QSystemTrayIcon):
    def __init__(
        self, 
        icon: QIcon, 
        calendar_service: CalendarService,
        current_day: Day,
        group: str
    ):
        super().__init__()
        
        self.calendar_service = calendar_service
        self.current_day = current_day
        self.group = group
        
        self.setIcon(icon)
        self.setToolTip(None)
        
        self._setup_menu()
        self._setup_tooltip()
        self._setup_timers()
    
    def _setup_menu(self) -> None:
        menu = QMenu()
        
        update_action = QAction("Обновить")
        update_action.triggered.connect(self._update_calendar)
        menu.addAction(update_action)
        
        exit_action = QAction("Выход")
        exit_action.triggered.connect(self._quit_application)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def _setup_tooltip(self) -> None:
        events = self.calendar_service.get_events_for_day(self.current_day)
        text = PairFormatter.format_events(self.current_day.date, events, self.group)

        self.tooltip = TrayTooltip(text, self, self.group)
        self.tooltip.setText(text, events, self.current_day.date)

        self.tooltip.prev_btn.clicked.connect(lambda: self._change_day(-1))
        self.tooltip.next_btn.clicked.connect(lambda: self._change_day(1))
    
    def _setup_timers(self) -> None:
        self.hover_timer = QTimer()
        self.hover_timer.setInterval(100)
        self.hover_timer.timeout.connect(self._check_hover)
        self.hover_timer.start()
        
        self.show_timer = QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._hover_accept)
    
    def _check_hover(self) -> None:
        if not self.show_timer.isActive():
            self.show_timer.start(800)
    
    def _hover_accept(self) -> None:
        cursor_pos = QCursor.pos()
        trect = self.tooltip.geometry()
        trect.setHeight(trect.height() + 8)
        
        if self.geometry().contains(cursor_pos):
            if not self.tooltip.isVisible():
                self.tooltip.show_above()
        elif not trect.contains(cursor_pos):
            self.tooltip.hide_tooltip()
    
    def _change_day(self, n: int) -> None:
        self.current_day = self.current_day.add_days(n)
        events = self.calendar_service.get_events_for_day(self.current_day)
        text = PairFormatter.format_events(self.current_day.date, events, self.group)
        self.tooltip.setText(text, events, self.current_day.date)
    
    def _update_calendar(self) -> None:
        self.calendar_service.load_calendar(self.group)
        self.current_day = Day.today()
        events = self.calendar_service.get_events_for_day(self.current_day)
        text = PairFormatter.format_events(self.current_day.date, events, self.group)
        self.tooltip.setText(text, events, self.current_day.date)
    
    def _quit_application(self) -> None:
        self.hide()
        QApplication.quit()