"""
notif.py

Written by Mason Schuster, 2025
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QTimer

class Notif(QWidget):
    def __init__(self, message, timeout_ms=5000):
        super().__init__()      
        self.setWindowTitle("Notification")
        self.setFixedSize(300, 100)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        #QTimer.singleShot(timeout_ms, self.close)

        notif_label = QLabel(message)
        notif_label.setAlignment(Qt.AlignCenter)
        notif_label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(notif_label)
        self.setLayout(layout)
