"""
successNotif.py

Written by Mason Schuster, 2025
"""

import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer

class SuccessNotif(QWidget):
    def __init__(self, message, pages, file_selections):
        super().__init__()      
        self.setWindowTitle("Notification")
        self.setFixedSize(300, 200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.pages = pages
        self.file_selections = file_selections
        self.results_proc = None


        # *************************
        #         BUTTONS
        # *************************
        # Return Home
        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self.go_home)
        self.home_button.setFixedSize(175, 30)

        # Run Different Simulation
        self.run_different_button = QPushButton("Run Different Simulation")
        self.run_different_button.clicked.connect(self.run_different_simulation)
        self.run_different_button.setFixedSize(175, 30)

        # View Results (keeps notif open)
        self.view_results_button = QPushButton("View Results")
        self.view_results_button.clicked.connect(self.view_results)
        self.view_results_button.setFixedSize(175, 30)

        # Button Layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.run_different_button)
        button_layout.addWidget(self.view_results_button)
        button_layout.setAlignment(Qt.AlignCenter)

        # *************************
        #       MAIN LAYOUT
        # *************************

        # Label
        notif_label = QLabel(message)
        notif_label.setAlignment(Qt.AlignCenter)
        notif_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(notif_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    # *************************
    #       FUNCTIONS
    # *************************
    def go_home(self):
        for page in self.pages:
            if page != "home_page":
                self.pages[page].close()

        self.pages["home_page"].show()
        self.close()
    
    def run_different_simulation(self):
        if "custom_agro_page" in self.pages:
            self.pages["custom_agro_page"].close()

        self.pages["agro_page"].show()
        self.close()

    def view_results(self):
        if self.results_proc and self.results_proc.poll() is None:
            return

        try:
            print("-WOFOST- Opening plot display")
            print(f"-WOFOST- Command: python3 gui/plotDisplay.py -f {self.file_selections["save_folder"]}/",)
            self.results_proc = subprocess.Popen([
                "python3", "-m", "gui.plotDisplay",
                "-f", f"{self.file_selections["save_folder"]}/",
            ])
        except subprocess.CalledProcessError as e:
            print(f"-WOFOST- Plot display failed with error: {e}")
