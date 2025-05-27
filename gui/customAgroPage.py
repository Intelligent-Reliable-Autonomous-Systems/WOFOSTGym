import os
import yaml
import subprocess
from notif import Notif

from PySide6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QCheckBox,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QTextEdit,
    QSizePolicy
)
from PySide6.QtCore import QSize, Qt

AGRO_FOLDER_PATH = "env_config/agro"
CROP_FOLDER_PATH = "env_config/crop"
SITE_FOLDER_PATH = "env_config/site"

class CustomAgro(QWidget):
    def __init__(self, pages, env_selections, file_selections):
        super().__init__()
        self.setWindowTitle("Custom Agromanagement Configuration")
        self.setFixedSize(400, 400)
        self.env_selections = env_selections
        self.file_selections = file_selections
        self.pages = pages
        self.pages["custom_agro_page"] = self

        # *************************
        #       VARIABLES
        # *************************

        # ===== CROPS =====
        crops = QGroupBox("")
        crops_layout = QVBoxLayout()

        # Crop Names
        self.crops_label = QLabel("Available Crops:")
        self.crops_label.setFixedSize(QSize(125, 30))
        self.crops_dropdown = QComboBox()
        self.crops_dropdown.setFixedSize(QSize(200, 30))
        self.crops_dropdown.currentIndexChanged.connect(self.load_crop_varieties)
        
        crop_names_layout = QHBoxLayout()
        crop_names_layout.addWidget(self.crops_label)
        crop_names_layout.addWidget(self.crops_dropdown)
        crop_names_layout.addStretch()

        # Crop Varieties
        self.crops_varieties_label = QLabel("Crop Varieties:")
        self.crops_varieties_label.setFixedSize(QSize(125, 30))
        self.crop_varieties_dropdown = QComboBox()
        self.crop_varieties_dropdown.setFixedSize(QSize(200, 30))

        crops_varieties_layout = QHBoxLayout()
        crops_varieties_layout.addWidget(self.crops_varieties_label)
        crops_varieties_layout.addWidget(self.crop_varieties_dropdown)
        crops_varieties_layout.addStretch()

        # Main Crop Layout
        crops_layout.addLayout(crop_names_layout)
        crops_layout.addLayout(crops_varieties_layout)
        crops.setLayout(crops_layout)    

        # ===== SITES =====
        sites = QGroupBox("")
        sites_layout = QVBoxLayout()

        # Site Names
        self.sites_label = QLabel("Available Sites:")
        self.sites_label.setFixedSize(QSize(125, 30))
        self.sites_dropdown = QComboBox()
        self.sites_dropdown.setFixedSize(QSize(200, 30))
        self.sites_dropdown.currentIndexChanged.connect(self.load_site_variations)

        site_layout = QHBoxLayout()
        site_layout.addWidget(self.sites_label)
        site_layout.addWidget(self.sites_dropdown)
        site_layout.addStretch()

        # Site Variations
        self.site_variations_label = QLabel("Site Variations:")
        self.site_variations_label.setFixedSize(QSize(125, 30))
        self.site_variations_dropdown = QComboBox()
        self.site_variations_dropdown.setFixedSize(QSize(200, 30))

        site_variations_layout = QHBoxLayout()
        site_variations_layout.addWidget(self.site_variations_label)
        site_variations_layout.addWidget(self.site_variations_dropdown)
        site_variations_layout.addStretch()

        # Main Site Layout
        sites_layout.addLayout(site_layout)
        sites_layout.addLayout(site_variations_layout)
        sites.setLayout(sites_layout)

        # ===== LOAD FILES =====
        self.load_crop_yaml_files()
        self.load_site_yaml_files()
        self.crops_dropdown.setCurrentIndex(-1)
        self.sites_dropdown.setCurrentIndex(-1)

        # *************************
        #         BUTTONS
        # *************************
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        run_sim_button = QPushButton("Run Simulation")
        run_sim_button.clicked.connect(self.run_simulation)

        # *************************
        #       MAIN LAYOUT
        # *************************
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(back_button)
        layout.addWidget(crops)
        layout.addWidget(sites)
        layout.addWidget(run_sim_button)
        self.setLayout(layout)

    # *************************
    #       FUNCTIONS
    # *************************
    # ===== CROPS =====
    def load_crop_yaml_files(self):
        if not os.path.isdir(CROP_FOLDER_PATH):
            print("Invalid crop folder path during crop YAML loading")
            return

        file_path = os.path.join(CROP_FOLDER_PATH, "crops.yaml")
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            self.crop_yaml_files = [crop for crop in data.get('available_crops', [])]
        except Exception as e:
            print(f"Error reading crop YAML file: {e}")
            self.crop_yaml_files = []

        if not self.crop_yaml_files:
            print("No crop YAML files found")
        else:
            self.crops_dropdown.addItems(self.crop_yaml_files)

    def load_crop_varieties(self):
        crop_name = self.crops_dropdown.currentText()
        if not crop_name or crop_name == "":
            self.crop_varieties = []
            return

        file_path = os.path.join(CROP_FOLDER_PATH, f"{crop_name}.yaml")
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            self.crop_varieties = data.get('CropParameters', {}).get('Varieties', {}).keys()

        except Exception as e:
            print(f"Error reading crop variations: {e}")
            self.crop_varieties = []

        self.crop_varieties_dropdown.clear()
        if self.crop_varieties:
            self.crop_varieties_dropdown.addItems(self.crop_varieties)
        else:
            self.crop_varieties_dropdown.addItem("No varieties available")
        self.crop_varieties_dropdown.setCurrentIndex(-1)

    # ===== SITES =====
    def load_site_yaml_files(self):
        if not os.path.isdir(SITE_FOLDER_PATH):
            print("Invalid site folder path during YAML loading")
            return

        file_path = os.path.join(SITE_FOLDER_PATH, "sites.yaml")
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            self.site_yaml_files = [site for site in data.get('available_sites', [])]
        except Exception as e:
            print(f"Error reading site YAML file during load: {e}")
            self.site_yaml_files = []

        if not self.site_yaml_files:
            print("No site YAML files found")
        else:
            self.sites_dropdown.addItems(self.site_yaml_files)

    def load_site_variations(self):
        site_name = self.sites_dropdown.currentText()
        if not site_name or site_name == "":
            self.site_variations = []
            return

        file_path = os.path.join(SITE_FOLDER_PATH, f"{site_name}.yaml")
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            self.site_variations = data.get('SiteParameters', {}).get('Variations', {}).keys()

        except Exception as e:
            print(f"Error reading site variations: {e}")
            self.site_variations = []

        self.site_variations_dropdown.clear()
        if self.site_variations:
            self.site_variations_dropdown.addItems(self.site_variations)
        else:
            self.site_variations_dropdown.addItem("No variations available")
        self.site_variations_dropdown.setCurrentIndex(-1)

    # ===== RUN SIMULATION =====
    def run_simulation(self):
        crop_name = self.crops_dropdown.currentText()
        crop_variety = self.crop_varieties_dropdown.currentText()
        site_name = self.sites_dropdown.currentText()
        site_variation = self.site_variations_dropdown.currentText()

        if not crop_name or not crop_variety or not site_name or not site_variation:
            self.notif = Notif("Please select all options.")
            self.notif.show()
            return
        
        print("-WOFOST- Running custom agro simulation...")
        print("-WOFOST- Command: python3 test_wofost.py --save-folder {} --data-file {} --env-id {} --npk.ag.crop-name {} --npk.ag.crop-variety {} --npk.ag.site-name {} --npk.ag.site-variation {}".format(
            self.file_selections["save_folder"],
            self.file_selections["data_file"],
            self.env_selections["env_id"],
            crop_name,
            crop_variety,
            site_name,
            site_variation
        ))

        subprocess.run([
            "python3", "test_wofost.py",
            "--save-folder", self.file_selections["save_folder"] + "/",
            "--data-file", self.file_selections["data_file"],
            "--env-id", self.env_selections["env_id"],
            "--npk.ag.crop-name", crop_name,
            "--npk.ag.crop-variety", crop_variety,
            "--npk.ag.site-name", site_name,
            "--npk.ag.site-variation", site_variation,
        ])

    # ===== NAVIGATION =====
    def go_back(self):
        self.pages["agro_page"].show()
        self.close()