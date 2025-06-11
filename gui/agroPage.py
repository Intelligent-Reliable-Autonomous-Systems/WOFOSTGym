import os
import fnmatch
import yaml
import subprocess
from notif import Notif
from successNotif import SuccessNotif
from customConfigPage import CustomConfigurationPage
from trainAgentPage import TrainAgentPage

from PySide6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QFrame,
    QVBoxLayout, QLabel, QHBoxLayout, QTextEdit,
)
from PySide6.QtCore import QSize, Qt

AGRO_FOLDER_PATH = "env_config/agro"

class AgromanagementPage(QWidget):
    def __init__(self, pages, env_selections, file_selections):
        super().__init__()
        self.setWindowTitle("WOFOSTGym GUI")
        self.setFixedSize(500, 500)
        self.env_selections = env_selections
        self.file_selections = file_selections
        self.pages = pages
        self.pages["agro_page"] = self

        # **************************
        #        INPUTS
        # **************************
        # Available Agro YAMLs
        self.agros_label = QLabel("Available Configs:")
        self.agros_label.setFixedSize(QSize(125, 30))
        self.agros_dropdown = QComboBox()
        self.agros_dropdown.setFixedSize(QSize(200, 30))
        
        agros_layout = QHBoxLayout()
        agros_layout.addWidget(self.agros_label)
        agros_layout.addWidget(self.agros_dropdown)
        agros_layout.addStretch()

        # **************************
        #        AGRO INFO
        # **************************
        self.selected_agro_info = QTextEdit()
        self.selected_agro_info.setReadOnly(True)
        self.selected_agro_info.setFixedSize(QSize(400, 250))

        # *************************
        #        BUTTONS
        # *************************
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        run_sim_button = QPushButton("Run Simulation")
        run_sim_button.clicked.connect(self.run_sim)

        run_training_button = QPushButton("Run Training")
        run_training_button.clicked.connect(self.run_training)

        custom_agro_button = QPushButton("Create Custom Config")
        custom_agro_button.clicked.connect(self.create_custom)

        # Button Layout
        run_button_layout = QHBoxLayout()
        run_button_layout.setContentsMargins(0, 0, 0, 0)
        run_button_layout.setSpacing(10)
        run_button_layout.addStretch()
        run_button_layout.addWidget(run_sim_button)
        run_button_layout.addWidget(run_training_button)
        run_button_layout.addStretch()

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedHeight(2)

        button_layout = QVBoxLayout()
        button_layout.addLayout(run_button_layout)
        button_layout.addWidget(separator)
        button_layout.addWidget(custom_agro_button)
        button_layout.addStretch()

        # *************************
        #         LAYOUT
        # *************************
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.header_label = QLabel("Agro File Selection")
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.header_label.setFixedHeight(20)

        layout.addWidget(back_button)
        layout.addWidget(self.header_label)
        layout.addLayout(agros_layout)
        layout.addWidget(self.selected_agro_info, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

        # *************************
        #      INITIALIZATION
        # *************************
        self.load_agro_yaml_files()
        self.agros_dropdown.setCurrentIndex(-1)

        # *************************
        #        SIGNALS
        # *************************
        self.agros_dropdown.currentIndexChanged.connect(self.read_selected_yaml)

    # *************************
    #        FUNCTIONS
    # *************************
    def load_agro_yaml_files(self):
        if not os.path.isdir(AGRO_FOLDER_PATH):
            print("-WOFOST- Invalid agro folder path")
            return

        self.yaml_files = [
            f for f in os.listdir(AGRO_FOLDER_PATH)
            if fnmatch.fnmatch(f, "*.yaml") or fnmatch.fnmatch(f, "*.yml")
        ]

        if not self.yaml_files:
            self.agros_dropdown.addItem("No YAML files found")
        else:
            self.agros_dropdown.addItems(self.yaml_files)

    def read_selected_yaml(self):
        index = self.agros_dropdown.currentIndex()
        if index < 0 or not self.yaml_files:
            return

        file_name = self.yaml_files[index]
        file_path = os.path.join(AGRO_FOLDER_PATH, file_name)

        try:
            with open(file_path, 'r') as yaml_file:
                self.yaml_data = yaml.safe_load(yaml_file)
                text_data = yaml.dump(self.yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
                self.selected_agro_info.setPlainText(text_data)
        except Exception as e:
            print(f"-WOFOST- Error reading agro YAML file: {e}")

    def check_input(self):
        agro_file = self.agros_dropdown.currentText()
        if not agro_file:
            self.notif = Notif("Please select an agro configuration.")
            self.notif.show()
            return False

        cycle = self.env_selections.get("cycle")
        crop = self.yaml_data.get("AgroManagement", {}).get("CropCalendar", {}).get("crop_name", "").lower()
        if cycle == "Annual" and crop in ["grape", "jujube", "pear"]:
            self.notif = Notif("Annual environment does not support grape, jujube, or pear.")
            self.notif.show()
            return False
        elif cycle == "Perennial" and crop not in ["jujube", "pear"]:
            self.notif = Notif("Perennial environment only supports jujube and pear.")
            self.notif.show()
            return False
        elif cycle == "Grape Specific" and crop != "grape":
            self.notif = Notif("Grape specific environment only supports grape.")
            self.notif.show()
            return False
        elif cycle == "Annual - Multi Farm" and crop in ["grape", "jujube", "pear"]:
            self.notif = Notif("Annual - Multi Farm environment does not support grape, jujube, or pear.")
            self.notif.show()
            return False
        elif cycle == "Perennial - Multi Farm" and crop not in ["jujube", "pear"]:
            self.notif = Notif("Perennial - Multi Farm environment only supports jujube and pear.")
            self.notif.show()
            return False
        return True
    

    def run_sim(self):
        if not self.check_input():
            return
        agro_file = self.agros_dropdown.currentText()
        try:
            print("-WOFOST- Running agro simulation...")
            print("-WOFOST- Command: python3 test_wofost.py --save-folder {}/ --data-file {} --env-id {} --agro-file {}".format(
                self.file_selections["save_folder"],
                self.file_selections["data_file"],
                self.env_selections["env_id"],
                agro_file
            ))
            subprocess.run([
                "python3", "test_wofost.py",
                "--save-folder", f"{self.file_selections['save_folder']}/",
                "--data-file", f"{self.file_selections['data_file']}",
                "--env-id", f"{self.env_selections['env_id']}",
                "--agro-file", f"{self.agros_dropdown.currentText()}"
            ], check=True)

            self.successNotif = SuccessNotif(message="Simulation completed", pages=self.pages, file_selections=self.file_selections)
            self.successNotif.show()
            self.close()
            print("-WOFOST- Simulation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"-WOFOST- Simulation failed with error: {e}")
            self.notif = Notif("Simulation failed.")
            self.notif.show()
            self.pages["env_page"].close()
            self.close()
            return
    
    def run_training(self):
        if not self.check_input():
            return
        self.env_selections["agro_file"] = self.agros_dropdown.currentText()
        self.train_agent_page = TrainAgentPage(
            pages=self.pages,
            env_selections=self.env_selections,
            file_selections=self.file_selections,
            return_loc="agro_page"
        )
        self.train_agent_page.show()
        self.hide()
  
    def create_custom(self):
        self.custom_agro = CustomConfigurationPage(pages=self.pages, env_selections=self.env_selections, file_selections=self.file_selections)
        self.custom_agro.show()
        self.hide()

    def go_back(self):
        self.pages["env_page"].show()
        self.close()