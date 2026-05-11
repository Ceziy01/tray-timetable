from PyQt6.QtGui import QIcon, QColor, QPainter, QImage, QPixmap
from PyQt6.QtCore import Qt

class IconService:
    @staticmethod
    def colorize_icon(icon_path: str, color: QColor, size: int = 32) -> QIcon:
        icon = QIcon(icon_path)
        pixmap = icon.pixmap(size, size)

        image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        new_pixmap = QPixmap(size, size)
        new_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(new_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawImage(0, 0, image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(new_pixmap.rect(), color)
        painter.end()
        
        return QIcon(new_pixmap)
    
    @staticmethod
    def invert_icon(icon_path: str) -> QIcon:
        pixmap = QPixmap(icon_path)
        image = pixmap.toImage()
        image.invertPixels()
        inverted_pixmap = QPixmap.fromImage(image)
        return QIcon(inverted_pixmap)