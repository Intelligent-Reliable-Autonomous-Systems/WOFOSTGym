"""
genDataPage.py

Written by Mason Schuster, 2025
"""

import os
import webbrowser
import subprocess
from gui.notif import Notif
from gui.viewLogsPage import ViewLogsPage

from PySide6.QtWidgets import (
    QWidget, QPushButton,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QComboBox
)
from PySide6.QtCore import QSize, Qt

class ViewDataPage(QWidget):
    def __init__(self, pages, file_selections):
        super().__init__()
        self.setWindowTitle("WOFOSTGym GUI")
        self.setFixedSize(500, 500)
        self.file_selections = file_selections
        self.pages = pages
        self.pages["view_data_page"] = self

        # **************************
        #        INPUTS
        # **************************

        # *************************
        #        BUTTONS
        # *************************

        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        view_logs_button = QPushButton("View Logs")
        view_logs_button.clicked.connect(self.view_logs)

        # *************************
        #        LAYOUT
        # *************************
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.header_label = QLabel("View Data")
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.header_label.setFixedHeight(30)

        main_layout.addWidget(back_button)
        main_layout.addWidget(self.header_label)
        main_layout.addWidget(view_logs_button)
        main_layout.addStretch()
        main_layout.setAlignment(Qt.AlignTop)

        self.setLayout(main_layout)


    # *************************
    #        FUNCTIONS
    # *************************
    def view_logs(self):
            if not os.path.isdir(self.file_selections["save_folder"]):
                print("-WOFOST- No training logs found in: " + self.file_selections["save_folder"])
                self.notif = Notif("No training logs found in given save folder.")
                self.notif.show()
                return

            self.view_logs_page = ViewLogsPage(pages=self.pages, file_selections=self.file_selections)
            self.view_logs_page.show()
            self.hide()

    def go_back(self):
        self.pages["home_page"].show()
        self.close()