from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QPalette
from datetime import datetime, timedelta

from BlurWindow.blurWindow import GlobalBlur

from .styles import BTN_STYLE, TOOLTIP_STYLE

class ProgressBorder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
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
            bg_color.setAlpha(15)
            painter.fillRect(self.rect(), bg_color)
            return
        
        bg_color = QColor(self.accent_color)
        bg_color.setAlpha(40)
        painter.fillRect(self.rect(), bg_color)
      
        if self.progress > 0:
            progress_width = int(self.width() * self.progress / 100)
            progress_rect = QRect(0, 0, progress_width, self.height())
            fg_color = QColor(self.accent_color)
            fg_color.setAlpha(220)
            painter.fillRect(progress_rect, fg_color)

class TrayTooltip(QWidget):
    def __init__(self, text, parent, group):
        super().__init__()
        self.parent = parent
        self.group = group
        self.current_events = []
        self.current_day_date = None
        
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(TOOLTIP_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 4)
        layout.setSpacing(2)

        self.progress_border = ProgressBorder(self)
        layout.addWidget(self.progress_border)
        
        self.label = QLabel(text)
        self.label.setStyleSheet("border: none; padding: 4px;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        btn_l = QHBoxLayout()
        btn_l.setSpacing(15)
        
        self.prev_btn = QPushButton("<")
        self.prev_btn.setStyleSheet(BTN_STYLE)
        self.prev_btn.setFixedSize(22, 22)
        btn_l.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton(">")
        self.next_btn.setStyleSheet(BTN_STYLE)
        self.next_btn.setFixedSize(22, 22)
        btn_l.addWidget(self.next_btn)
        
        layout.addLayout(btn_l)
        
        self.setLayout(layout)
        self.adjustSize()
        
        hwnd = self.winId()
        GlobalBlur(hwnd, Acrylic=True, hexColor="A0515151")
    
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_progress)
        self.update_timer.start(30000)
    
    def _is_today(self):
        if not self.current_day_date:
            return False
        return self.current_day_date == datetime.now().date()
    
    def _find_current_pair(self):
        if not self._is_today():
            return None
        
        now = datetime.now().time()
        today = datetime.now().date()
        
        for event in self.current_events:
            if event[1] and isinstance(event[1], str):
                try:
                    time_str = event[1]
                    start_time = datetime.strptime(time_str, "%H:%M").time()
                    
                    start_dt = datetime.combine(today, start_time)
                    end_dt = start_dt + timedelta(minutes=90)
                    
                    if start_time <= now <= end_dt.time():
                        return (event, start_time, end_dt.time())
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
    
    def setText(self, text, events=None, day_date=None):
        self.label.setText(text)
        if events is not None:
            self.current_events = events
        if day_date is not None:
            self.current_day_date = day_date
        
        self._update_progress()
        self.adjustSize()
        self.show_above()
    
    def show_above(self):
        self.adjustSize()
        trpos = self.parent.geometry().getRect()
        tpos = self.geometry().getRect()
        trx = trpos[0]
        trry = trpos[1]
        trw = trpos[2]
        
        tw = tpos[2]
        th = tpos[3]
        
        self.move(QPoint(trx - tw // 2 + trw // 2, trry - th - 8))
        self.show()
    
    def hide_tooltip(self):
        if self.isVisible():
            self.hide()