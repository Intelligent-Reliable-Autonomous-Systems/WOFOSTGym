"""
homePage.py

Written by Mason Schuster, 2025
"""

import sys
from gui.envPage import EnvironmentPage
from gui.notif import Notif
from gui.genDataPage import ViewDataPage

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import QSize, Qt

SAVES_FOLDER_NAME = "saves"

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WOFOSTGym GUI")
        self.setFixedSize(500, 500)
        self.pages = {"home_page": self}

        # *************************
        #        HEADERS
        # *************************

        # Main header
        self.header_label = QLabel("WOFOSTGym Simulation Tool")
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.header_label.setFixedHeight(20)

        # Description
        self.description_label = QLabel("This is a graphical user interface (GUI) built on top of the WOFOSTGym crop growth model. "
            "It allows users to generate data, simulate agricultural environments, and train reinforcement learning agents. \n"
            "*This tool is designed for research and educational use.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: gray;")
        self.description_label.setFixedHeight(60)

        # *************************
        #        INPUTS
        # *************************
        inputs = QGroupBox("")
        inputs_layout = QVBoxLayout()

        # Save Folder
        self.save_folder_loc_input_box = QLineEdit()
        self.save_folder_loc_input_box.setPlaceholderText("Enter folder location...")
        self.save_folder_loc_input_box.setFixedSize(QSize(200, 30))
        self.save_folder_loc_label = QLabel("Save Folder:")
        self.save_folder_loc_label.setFixedSize(QSize(100, 30))

        save_folder_layout = QHBoxLayout()
        save_folder_layout.addWidget(self.save_folder_loc_label)
        save_folder_layout.addWidget(self.save_folder_loc_input_box)

        # Data File Name
        self.data_file_name_input_box = QLineEdit()
        self.data_file_name_input_box.setPlaceholderText("Enter file name...")
        self.data_file_name_input_box.setFixedSize(QSize(200, 30))
        self.data_file_name_label = QLabel("Data File Name:")
        self.data_file_name_label.setFixedSize(QSize(100, 30))

        data_file_layout = QHBoxLayout()
        data_file_layout.addWidget(self.data_file_name_label)
        data_file_layout.addWidget(self.data_file_name_input_box)
        
        inputs_layout.addLayout(save_folder_layout)
        inputs_layout.addLayout(data_file_layout)
        inputs_layout.setContentsMargins(10, 10, 10, 10)
        inputs_layout.setSpacing(10)
        inputs.setFixedSize(QSize(400, 200))
        inputs.setLayout(inputs_layout)

        # *************************
        #        BUTTONS
        # *************************
        self.gen_data_button = QPushButton("Generate Data")
        self.gen_data_button.clicked.connect(self.nav_gen_data)

        self.run_process_button = QPushButton("Run Sim/Train")
        self.run_process_button.clicked.connect(self.run_process)

        self.about_page_button = QPushButton("More Information")
        self.about_page_button.clicked.connect(self.open_about_page)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.gen_data_button)
        button_layout.addWidget(self.run_process_button)

        # *************************
        #        MAIN LAYOUT
        # *************************
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(self.header_label)
        main_layout.addWidget(self.description_label)
        main_layout.addWidget(self.about_page_button)
        main_layout.addWidget(inputs, alignment=Qt.AlignCenter)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


    # *************************
    #        FUNCTIONS
    # *************************
    def nav_gen_data(self):
        if not self.save_folder_loc_input_box.text() or not self.data_file_name_input_box.text():
            self.notif = Notif("Please fill in all fields.")
            self.notif.show()
            return
        
        file_selections = {
            "save_folder": "sim_runs/" + self.save_folder_loc_input_box.text(),
            "data_file": self.data_file_name_input_box.text(),
        }

        self.gen_data_page = ViewDataPage(pages=self.pages, file_selections=file_selections)
        self.gen_data_page.show()
        self.hide()

    def run_process(self):
        if not self.save_folder_loc_input_box.text() or not self.data_file_name_input_box.text():
            self.notif = Notif("Please fill in all fields.")
            self.notif.show()
            return
        
        file_selections = {
            "save_folder": "sim_runs/" + self.save_folder_loc_input_box.text(),
            "data_file": self.data_file_name_input_box.text(),
        }

        self.env_page = EnvironmentPage(pages=self.pages, file_selections=file_selections)
        self.env_page.show()
        self.hide()

    def open_about_page(self):
        self.about_page = AboutPage(self.pages)
        self.about_page.show()
        self.hide()


class AboutPage(QWidget):
    def __init__(self, pages):
        super().__init__()
        self.setWindowTitle("About WOFOSTGym")
        self.setFixedSize(500, 500)
        self.pages = pages
        self.pages["about_page"] = self

        # *************************
        #        CONTENT
        # *************************

        self.desc_label = QLabel("Summary")
        self.desc_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.desc_label.setFixedHeight(30)
        self.desc = QLabel(
            "WOFOSTGym is a crop simulation environment for training reinforcement learning (RL) agents to optimize "
            "agricultural decisions across multiple crops and farms. It supports 23 annual and 2 perennial crops, enabling "
            "multi-year agromanagement learning with challenges like partial observability and delayed feedback. "
            "WOFOSTGym fills a gap in existing simulators by including multi-farm and perennial crop support and features "
            "a standard RL interface to make it accessible to non-experts."
        )
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("font-size: 13px; color: gray;")

        self.desc_layout = QVBoxLayout()
        self.desc_layout.setContentsMargins(10, 10, 10, 10)
        self.desc_layout.setSpacing(10)
        self.desc_layout.addWidget(self.desc_label)
        self.desc_layout.addWidget(self.desc)

        self.links_label = QLabel("Helpful Links")
        self.links_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.links_label.setFixedHeight(20)
        self.links = QLabel(
            """
            <div style='font-size: 13px; color: gray;'>
                <p><a href='https://intelligent-reliable-autonomous-systems.github.io/WOFOSTGym-Docs/installation.html' style='color:#2a6bd6;'>Documentation</a></p>
                <p><a href='https://intelligent-reliable-autonomous-systems.github.io/WOFOSTGym-Site/' style='color:#2a6bd6;'>Website</a></p>
                <p><a href='https://arxiv.org/abs/2502.19308' style='color:#2a6bd6;'>Research Paper</a></p>
                <p><a href='https://github.com/Intelligent-Reliable-Autonomous-Systems/WOFOSTGym' style='color:#2a6bd6;'>GitHub Repository</a></p>
            </div>
            """
        )
        self.links.setOpenExternalLinks(True)
        self.links.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.links.setWordWrap(True)

        self.links_layout = QVBoxLayout()
        self.links_layout.setContentsMargins(10, 10, 10, 10)
        self.links_layout.setSpacing(10)
        self.links_layout.addWidget(self.links_label)
        self.links_layout.addWidget(self.links)

        # *************************
        #        BUTTONS
        # *************************
        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(QSize(50, 30))
        self.back_button.clicked.connect(self.go_back)

        # *************************
        #        LAYOUT
        # *************************
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(self.back_button)
        layout.addLayout(self.desc_layout)
        layout.addLayout(self.links_layout)
        self.setLayout(layout)

    # *********************
    #       FUNCTIONS
    # *********************
    def go_back(self):
        self.pages["home_page"].show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
