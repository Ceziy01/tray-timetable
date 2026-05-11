import ctypes
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPalette
from BlurWindow.blurWindow import GlobalBlur
from datetime import datetime, timedelta

from src.ui.styles import TOOLTIP_STYLE, BUTTON_STYLE

class ProgressBorder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self.setSizePolicy(Qt.SizePolicy.Policy.Expanding, Qt.SizePolicy.Policy.Fixed)
        self.progress = 0
        self.is_active = False
        
        app = QApplication.instance()
        if app:
            palette = app.palette()
            self.accent_color = palette.color(QPalette.ColorRole.Accent)
        else:
            self.accent_color = QColor(0, 120, 212)
    
    def set_progress(self, value: int):
        self.progress = max(0, min(100, value))
        self.is_active = True
        self.update()
    
    def set_inactive(self):
        self.is_active = False
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.is_active:
            bg_color = QColor(self.accent_color)
            bg_color.setAlpha(10)
            painter.fillRect(self.rect(), bg_color)
            return
        
        bg_color = QColor(self.accent_color)
        bg_color.setAlpha(30)
        painter.fillRect(self.rect(), bg_color)
        
        if self.progress > 0:
            progress_width = int(self.width() * self.progress / 100)
            progress_rect = QRect(0, 0, progress_width, self.height())
            fg_color = QColor(self.accent_color)
            fg_color.setAlpha(200)
            painter.fillRect(progress_rect, fg_color)

class TrayTooltip(QWidget):
    def __init__(self, text: str, parent, group: str):
        super().__init__()
        
        self.parent = parent
        self.group = group
        self.current_events = []
        self.current_day_date = None

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_progress)
        self.update_timer.start(30000)
        
        self._setup_window_flags()
        self._setup_ui(text)
        self._apply_blur_effect()
    
    def _setup_window_flags(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    
    def _setup_ui(self, text: str) -> None:
        self.setStyleSheet(TOOLTIP_STYLE)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 0, 2, 4)
        main_layout.setSpacing(2)

        self.progress_border = ProgressBorder(self)
        main_layout.addWidget(self.progress_border)
    
        self.label = QLabel(text)
        self.label.setStyleSheet("border: none; padding: 4px; color: white;")
        self.label.setWordWrap(True)
        main_layout.addWidget(self.label)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(4, 0, 4, 0)
        button_layout.setSpacing(10)
        
        self.prev_btn = QPushButton("<")
        self.prev_btn.setStyleSheet(BUTTON_STYLE)
        self.prev_btn.setFixedSize(20, 20)
        button_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton(">")
        self.next_btn.setStyleSheet(BUTTON_STYLE)
        self.next_btn.setFixedSize(20, 20)
        button_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(button_layout)
      
        self.setFixedWidth(260)
        self.setMaximumHeight(250)
    
    def _apply_blur_effect(self) -> None:
        hwnd = int(self.winId())
        GlobalBlur(hwnd, Acrylic=True, hexColor="A0515151")
    
    def _is_today(self) -> bool:
        if not self.current_day_date:
            return False
        return self.current_day_date == datetime.now().date()
    
    def _find_current_pair(self):
        if not self._is_today():
            return None
        
        now = datetime.now().time()
        today = datetime.now().date()
        
        for event in self.current_events:
            if event[1]:
                try:
                    time_str = event[1]
                    start_time = datetime.strptime(time_str, "%H:%M").time()
                    
                    start_dt = datetime.combine(today, start_time)
                    end_dt = start_dt + timedelta(minutes=90)
                    
                    if start_dt.time() <= now <= end_dt.time():
                        return (event, start_dt.time(), end_dt.time())
                except:
                    continue
        return None
    
    def _update_progress(self):
        if not self._is_today():
            self.progress_border.set_inactive()
            return
        
        current_pair_data = self._find_current_pair()
        
        if current_pair_data:
            _, start_time, end_time = current_pair_data
            today = datetime.now().date()
            now = datetime.now().time()
            
            start_dt = datetime.combine(today, start_time)
            end_dt = datetime.combine(today, end_time)
            now_dt = datetime.combine(today, now)
            
            total = (end_dt - start_dt).total_seconds()
            elapsed = (now_dt - start_dt).total_seconds()
            
            progress = int((elapsed / total) * 100)
            self.progress_border.set_progress(progress)
        else:
            self.progress_border.set_inactive()
    
    def setText(self, text: str, events=None, day_date=None) -> None:
        self.label.setText(text)
        if events is not None:
            self.current_events = events
        if day_date is not None:
            self.current_day_date = day_date

        self._update_progress()
        self.adjustSize()
    
    def show_above(self) -> None:
        self.adjustSize()

        parent_rect = self.parent.geometry()
        
        x = parent_rect.x() + (parent_rect.width() // 2) - (self.width() // 2)
        y = parent_rect.y() - self.height() - 5  
        screen_rect = QApplication.primaryScreen().availableGeometry()
        x = max(5, min(x, screen_rect.width() - self.width() - 5))

        if y < 5:
            y = parent_rect.y() + parent_rect.height() + 5
        
        self.move(x, y)
        self.show()
    
    def hide_tooltip(self) -> None:
        if self.isVisible():
            self.hide()
    
    def sizeHint(self) -> QSize:
        return QSize(260, min(self.label.sizeHint().height() + 50, 250))