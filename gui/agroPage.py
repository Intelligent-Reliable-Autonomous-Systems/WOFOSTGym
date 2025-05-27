import os
import fnmatch
import yaml
import subprocess
from notif import Notif
from successNotif import SuccessNotif
from customAgroPage import CustomAgro

from PySide6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QCheckBox,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QTextEdit,
    QSizePolicy
)
from PySide6.QtCore import QSize, Qt

AGRO_FOLDER_PATH = "env_config/agro"


class AgromanagementPage(QWidget):
    def __init__(self, pages, env_selections, file_selections):
        super().__init__()
        self.setWindowTitle("Agromanagement Configuration")
        self.setFixedSize(400, 500)
        self.env_selections = env_selections
        self.file_selections = file_selections
        self.pages = pages
        self.pages["agro_page"] = self

        # ===== Variables =====

        # Available Agros
        self.agros_label = QLabel("Available Configs:")
        self.agros_label.setFixedSize(QSize(125, 30))
        self.agros_dropdown = QComboBox()
        self.agros_dropdown.setFixedSize(QSize(200, 30))
        
        agros_layout = QHBoxLayout()
        agros_layout.addWidget(self.agros_label)
        agros_layout.addWidget(self.agros_dropdown)
        agros_layout.addStretch()

        self.selected_agro_site_info = QTextEdit()
        self.selected_agro_site_info.setReadOnly(True)
        self.selected_agro_site_label = QLabel("Site Info:")
        self.selected_agro_crop_info = QTextEdit()
        self.selected_agro_crop_info.setReadOnly(True)
        self.selected_agro_crop_label = QLabel("Crop Info:")

        self.selected_agro_site_info.setFixedHeight(100)
        self.selected_agro_crop_info.setFixedHeight(100)

        agros_info_layout = QVBoxLayout()
        agros_info_layout.addWidget(self.selected_agro_site_label)
        agros_info_layout.addWidget(self.selected_agro_site_info)
        agros_info_layout.addWidget(self.selected_agro_crop_label)
        agros_info_layout.addWidget(self.selected_agro_crop_info)

        self.load_agro_yaml_files()
        self.agros_dropdown.setCurrentIndex(-1)
        self.agros_dropdown.currentIndexChanged.connect(self.read_selected_yaml)


        # ===== Buttons =====
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        run_sim_button = QPushButton("Run Simulation")
        run_sim_button.clicked.connect(self.run_simulation)

        custom_agro_button = QPushButton("Custom Agro")
        custom_agro_button.clicked.connect(self.run_custom_agro)


        # ===== Main Layout =====
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(back_button)
        layout.addLayout(agros_layout)
        layout.addLayout(agros_info_layout)
        layout.addWidget(run_sim_button)
        layout.addWidget(custom_agro_button)
        self.setLayout(layout)


    # ===== Functions =====
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
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)

            agm = data.get("AgroManagement", {})
            site = agm.get("SiteCalendar", {})
            crop = agm.get("CropCalendar", {})
            self.site = site
            self.crop = crop

            if not site or not crop:
                self.selected_agro_site_info.setText("No site information available.")
                self.selected_agro_crop_info.setText("No crop information available.")
                return
            
            site_data_formatted = (
                f"Name: {site.get('site_name', 'N/A')}\n"
                f"Variation: {site.get('site_variation', 'N/A')}\n"
                f"Location: {site.get('latitude', 'N/A')}, {site.get('longitude', 'N/A')}\n"
                f"Year: {site.get('year', 'N/A')}\n"
                f"Start/End: {site.get('site_start_date', 'N/A')} / {site.get('site_end_date')}"
            )    

            crop_data_formatted = (
                f"Name: {crop.get('crop_name', 'N/A')}\n"
                f"Variety: {crop.get('crop_variety', 'N/A')}\n"
                f"Start Date/Type: {crop.get('crop_start_date', 'N/A')} ({crop.get('crop_start_type', 'N/A')})\n"
                f"End Date/Type: {crop.get('crop_end_date', 'N/A')} ({crop.get('crop_end_type', 'N/A')})\n"
                f"Max Duration: {crop.get('max_duration', 'N/A')} days"
            )

            self.selected_agro_site_info.setText(site_data_formatted)
            self.selected_agro_crop_info.setText(crop_data_formatted)

        except Exception as e:
            print(f"-WOFOST- Error reading agro YAML file: {e}")

    def run_simulation(self):
        agro_file = self.agros_dropdown.currentText()
        if not agro_file:
            self.notif = Notif("Please select an agro configuration.")
            self.notif.show()
            return

        cycle = self.env_selections.get("cycle")
        if cycle == "Annual" and self.crop.get("crop_name").lower() in ["grape", "jujube", "pear"]:
            self.notif = Notif("Annual environment does not support grape, jujube, or pear.")
            self.notif.show()
            return
        elif cycle == "Perennial" and self.crop.get("crop_name").lower() not in ["jujube", "pear"]:
            self.notif = Notif("Perennial environment only supports jujube and pear.")
            self.notif.show()
            return
        elif cycle == "Grape Specific" and self.crop.get("crop_name").lower() != "grape":
            self.notif = Notif("Grape specific environment only supports grape.")
            self.notif.show()
            return
        elif cycle == "Annual - Multi Farm" and self.crop.get("crop_name").lower() in ["grape", "jujube", "pear"]:
            self.notif = Notif("Annual - Multi Farm environment does not support grape, jujube, or pear.")
            self.notif.show()
            return
        elif cycle == "Perennial - Multi Farm" and self.crop.get("crop_name").lower() not in ["jujube", "pear"]:
            self.notif = Notif("Perennial - Multi Farm environment only supports jujube and pear.")
            self.notif.show()
            return
        
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
        
    def run_custom_agro(self):
        self.custom_agro = CustomAgro(pages=self.pages, env_selections=self.env_selections, file_selections=self.file_selections)
        self.custom_agro.show()
        self.hide()

    def go_back(self):
        self.pages["env_page"].show()
        self.close()