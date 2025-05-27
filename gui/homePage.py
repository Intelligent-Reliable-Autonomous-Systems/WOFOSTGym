import sys
import subprocess
from envPage import EnvironmentPage
from trainAgentPage import TrainAgentPage
from notif import Notif

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import QSize

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # *************************
        #        INPUTS
        # *************************
        inputs = QGroupBox("")
        inputs_layout = QVBoxLayout()

        # ===== SAVE FOLDER LOCATION =====
        self.save_folder_loc_input_box = QLineEdit()
        self.save_folder_loc_input_box.setPlaceholderText("Enter folder location...")
        self.save_folder_loc_input_box.setFixedSize(QSize(200, 30))
        self.save_folder_loc_label = QLabel("Save Folder:")
        self.save_folder_loc_label.setFixedSize(QSize(100, 30))

        save_folder_layout = QHBoxLayout()
        save_folder_layout.addWidget(self.save_folder_loc_label)
        save_folder_layout.addWidget(self.save_folder_loc_input_box)

        ## ===== DATA FILE NAME =====
        self.data_file_name_input_box = QLineEdit()
        self.data_file_name_input_box.setPlaceholderText("Enter file name...")
        self.data_file_name_input_box.setFixedSize(QSize(200, 30))
        self.data_file_name_label = QLabel("Data File Name:")
        self.data_file_name_label.setFixedSize(QSize(100, 30))

        data_file_layout = QHBoxLayout()
        data_file_layout.addWidget(self.data_file_name_label)
        data_file_layout.addWidget(self.data_file_name_input_box)

        # ===== LAYOUT =====
        inputs_layout.addLayout(save_folder_layout)
        inputs_layout.addLayout(data_file_layout)
        inputs.setLayout(inputs_layout)

        # *************************
        #        BUTTONS
        # *************************
        self.gen_data_button = QPushButton("Generate Data")
        self.gen_data_button.clicked.connect(self.nav_gen_data)
        self.run_sim_button = QPushButton("Single Simulation")
        self.run_sim_button.clicked.connect(self.nav_single_sim)
        self.train_agent_button = QPushButton("Train Agent")
        self.train_agent_button.clicked.connect(self.nav_train_agent)
        # self.view_results_button = QPushButton("View Results")
        # self.view_results_button.clicked.connect(self.nav_view_results)

        for btn in [self.gen_data_button, self.run_sim_button, # self.view_results_button #
                    self.train_agent_button]:
            btn.setFixedSize(QSize(120, 30))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.gen_data_button)
        button_layout.addWidget(self.run_sim_button)
        button_layout.addWidget(self.train_agent_button)
        # button_layout.addWidget(self.view_results_button)
        button_layout.setSpacing(15)

        # *************************
        #        MAIN LAYOUT
        # *************************
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(inputs)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("WOFOSTGym GUI")
        self.setFixedSize(400, 200)

    # *************************
    #        FUNCTIONS
    # *************************
    def nav_gen_data(self):
        pass

    def nav_single_sim(self):
        file_selections = {
            "save_folder": self.save_folder_loc_input_box.text(),
            "data_file": self.data_file_name_input_box.text()
        }

        if not file_selections["save_folder"] or not file_selections["data_file"]:
            self.notif = Notif("Please fill in all fields.")
            self.notif.show()
            return

        self.env_page = EnvironmentPage(home_page=self, file_selections=file_selections)
        self.env_page.show()
        self.hide()

    def nav_train_agent(self):
        file_selections = {
            "save_folder": self.save_folder_loc_input_box.text(),
            "data_file": self.data_file_name_input_box.text()
        }

        if not file_selections["save_folder"]:
            self.notif = Notif("Please enter a save folder.")
            self.notif.show()
            return

        self.train_agent_page = TrainAgentPage(home_page=self, file_selections=file_selections)
        self.train_agent_page.show()
        self.hide()

    def nav_view_results(self):
        if not self.save_folder_loc_input_box.text():
            self.notif = Notif("Please provide a save folder to view results from.")
            self.notif.show()
            return
        try:
            subprocess.run([
                "python3", "gui/plotDisplay.py",
                "-f", f"{self.save_folder_loc_input_box.text()}/",
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Plot display failed with error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
