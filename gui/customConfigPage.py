import os
import yaml
import subprocess
from notif import Notif
from successNotif import SuccessNotif
from trainAgentPage import TrainAgentPage
import yamlHelper as ah

from PySide6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QLineEdit, QCheckBox, QDateEdit,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QTextEdit,
)
from PySide6.QtCore import QSize, QDate

AGRO_FOLDER_PATH = "env_config/agro"
CROP_FOLDER_PATH = "env_config/crop"
SITE_FOLDER_PATH = "env_config/site"

class CustomConfigurationPage(QWidget):
    def __init__(self, pages, env_selections, file_selections):
        super().__init__()
        self.setWindowTitle("Custom Configuration")
        self.setFixedSize(1000, 500)
        self.env_selections = env_selections
        self.file_selections = file_selections
        self.pages = pages
        self.pages["custom_config_page"] = self

        # *************************
        #       CROP INPUTS
        # *************************
        crops = QGroupBox("")
        crops_layout = QVBoxLayout()

        # Crop Name
        self.crops_label = QLabel("Available Crops:")
        self.crops_label.setFixedSize(QSize(125, 30))
        self.crops_dropdown = QComboBox()
        self.crops_dropdown.setFixedSize(QSize(200, 30))
        
        crop_names_layout = QHBoxLayout()
        crop_names_layout.addWidget(self.crops_label)
        crop_names_layout.addWidget(self.crops_dropdown)
        crop_names_layout.addStretch()

        # Crop Variety
        self.crops_varieties_label = QLabel("Crop Varieties:")
        self.crops_varieties_label.setFixedSize(QSize(125, 30))
        self.crop_varieties_dropdown = QComboBox()
        self.crop_varieties_dropdown.setFixedSize(QSize(200, 30))

        crops_varieties_layout = QHBoxLayout()
        crops_varieties_layout.addWidget(self.crops_varieties_label)
        crops_varieties_layout.addWidget(self.crop_varieties_dropdown)
        crops_varieties_layout.addStretch()

        # Crop End Type
        self.crop_end_type_label = QLabel("Crop End Type:")
        self.crop_end_type_label.setFixedSize(QSize(125, 30))
        self.crop_end_type_dropdown = QComboBox()
        self.crop_end_type_dropdown.addItems(["death", "max_duration"])
        self.crop_end_type_dropdown.setFixedSize(QSize(200, 30))

        crop_end_type_layout = QHBoxLayout()
        crop_end_type_layout.addWidget(self.crop_end_type_label)
        crop_end_type_layout.addWidget(self.crop_end_type_dropdown)
        crop_end_type_layout.addStretch()

        # Crop Max Duration
        self.crop_max_duration_label = QLabel("Crop Max Duration:")
        self.crop_max_duration_label.setFixedSize(QSize(125, 30))
        self.crop_max_duration_input = QLineEdit()

        crop_max_duration_layout = QHBoxLayout()
        crop_max_duration_layout.addWidget(self.crop_max_duration_label)
        crop_max_duration_layout.addWidget(self.crop_max_duration_input)
        crop_max_duration_layout.addStretch()

        # Crop Start Date
        self.crop_start_date_label = QLabel("Crop Start Date:")
        self.crop_start_date_label.setFixedSize(QSize(125, 30))
        self.crop_start_date_input = QDateEdit()
        self.crop_start_date_input.setDate(QDate(2020, 1, 1))
        self.crop_start_date_input.setCalendarPopup(True)
        self.crop_start_date_input.setDisplayFormat("yyyy-MM-dd")

        crop_start_date_layout = QHBoxLayout()
        crop_start_date_layout.addWidget(self.crop_start_date_label)
        crop_start_date_layout.addWidget(self.crop_start_date_input)
        crop_start_date_layout.addStretch()

        # Crop End Date
        self.crop_end_date_label = QLabel("Crop End Date:")
        self.crop_end_date_label.setFixedSize(QSize(125, 30))
        self.crop_end_date_input = QDateEdit()
        self.crop_end_date_input.setDate(QDate(2020, 12, 31))
        self.crop_end_date_input.setCalendarPopup(True)
        self.crop_end_date_input.setDisplayFormat("yyyy-MM-dd")

        crop_end_date_layout = QHBoxLayout()
        crop_end_date_layout.addWidget(self.crop_end_date_label)
        crop_end_date_layout.addWidget(self.crop_end_date_input)
        crop_end_date_layout.addStretch()

        # Main Crop Layout
        crops_layout.addLayout(crop_names_layout)
        crops_layout.addLayout(crops_varieties_layout)
        crops_layout.addLayout(crop_end_type_layout)
        crops_layout.addLayout(crop_max_duration_layout)
        crops_layout.addLayout(crop_start_date_layout)
        crops_layout.addLayout(crop_end_date_layout)
        crops.setLayout(crops_layout)    

        # *************************
        #       SITE INPUTS
        # *************************
        sites = QGroupBox("")
        sites_layout = QVBoxLayout()

        # Site Name
        self.sites_label = QLabel("Available Sites:")
        self.sites_label.setFixedSize(QSize(125, 30))
        self.sites_dropdown = QComboBox()
        self.sites_dropdown.setFixedSize(QSize(200, 30))

        site_layout = QHBoxLayout()
        site_layout.addWidget(self.sites_label)
        site_layout.addWidget(self.sites_dropdown)
        site_layout.addStretch()

        # Site Variation
        self.site_variations_label = QLabel("Site Variations:")
        self.site_variations_label.setFixedSize(QSize(125, 30))
        self.site_variations_dropdown = QComboBox()
        self.site_variations_dropdown.setFixedSize(QSize(200, 30))

        site_variations_layout = QHBoxLayout()
        site_variations_layout.addWidget(self.site_variations_label)
        site_variations_layout.addWidget(self.site_variations_dropdown)
        site_variations_layout.addStretch()

        # Site Latitude
        self.site_latitude_label = QLabel("Site Latitude:")
        self.site_latitude_label.setFixedSize(QSize(125, 30))
        self.site_latitude_input = QLineEdit()
        
        site_latitude_layout = QHBoxLayout()
        site_latitude_layout.addWidget(self.site_latitude_label)
        site_latitude_layout.addWidget(self.site_latitude_input)
        site_latitude_layout.addStretch()

        # Site Longitude
        self.site_longitude_label = QLabel("Site Longitude:")
        self.site_longitude_label.setFixedSize(QSize(125, 30))
        self.site_longitude_input = QLineEdit()

        site_longitude_layout = QHBoxLayout()
        site_longitude_layout.addWidget(self.site_longitude_label)
        site_longitude_layout.addWidget(self.site_longitude_input)
        site_longitude_layout.addStretch()

        # Site Year
        self.site_year_label = QLabel("Site Year:")
        self.site_year_label.setFixedSize(QSize(125, 30))
        self.site_year_input = QLineEdit()
        
        site_year_layout = QHBoxLayout()
        site_year_layout.addWidget(self.site_year_label)
        site_year_layout.addWidget(self.site_year_input)
        site_year_layout.addStretch()

        # Site Start Date
        self.site_start_date_label = QLabel("Site Start Date:")
        self.site_start_date_label.setFixedSize(QSize(125, 30))
        self.site_start_date_input = QDateEdit()
        self.site_start_date_input.setDate(QDate(2020, 1, 1))
        self.site_start_date_input.setCalendarPopup(True)
        self.site_start_date_input.setDisplayFormat("yyyy-MM-dd")

        site_start_date_layout = QHBoxLayout()
        site_start_date_layout.addWidget(self.site_start_date_label)
        site_start_date_layout.addWidget(self.site_start_date_input)
        site_start_date_layout.addStretch()

        # Site End Date
        self.site_end_date_label = QLabel("Site End Date:")
        self.site_end_date_label.setFixedSize(QSize(125, 30))
        self.site_end_date_input = QDateEdit()
        self.site_end_date_input.setDate(QDate(2020, 12, 31))
        self.site_end_date_input.setCalendarPopup(True)
        self.site_end_date_input.setDisplayFormat("yyyy-MM-dd")

        site_end_date_layout = QHBoxLayout()
        site_end_date_layout.addWidget(self.site_end_date_label)
        site_end_date_layout.addWidget(self.site_end_date_input)
        site_end_date_layout.addStretch()

        # Main Site Layout
        sites_layout.addLayout(site_layout)
        sites_layout.addLayout(site_variations_layout)
        sites_layout.addLayout(site_latitude_layout)
        sites_layout.addLayout(site_longitude_layout)
        sites_layout.addLayout(site_year_layout)
        sites_layout.addLayout(site_start_date_layout)
        sites_layout.addLayout(site_end_date_layout)
        sites.setLayout(sites_layout)

        # *************************
        #         BUTTONS
        # *************************
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        run_sim_button = QPushButton("Run Simulation")
        run_sim_button.clicked.connect(self.run_simulation)

        run_training_button = QPushButton("Run Training")
        run_training_button.clicked.connect(self.run_training)

        run_button_layout = QHBoxLayout()
        run_button_layout.addStretch()
        run_button_layout.addWidget(run_sim_button)
        run_button_layout.addWidget(run_training_button)
        run_button_layout.addStretch()

        # *************************
        #          LAYOUT
        # *************************
        # Sub
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(crops)
        dropdown_layout.addWidget(sites)

        self.agro_man_info = QTextEdit()
        self.agro_man_info.setReadOnly(True)

        sub_layout = QHBoxLayout()
        sub_layout.addLayout(dropdown_layout)
        sub_layout.addWidget(self.agro_man_info)

        # Misc
        self.yaml_name_label = QLabel("Agro File Name:")
        self.yaml_name_label.setFixedSize(QSize(125, 30))
        self.yaml_name_input = QLineEdit()

        yaml_name_layout = QHBoxLayout()
        yaml_name_layout.addWidget(self.yaml_name_label)
        yaml_name_layout.addWidget(self.yaml_name_input)
        yaml_name_layout.addStretch()

        self.save_file_checkbox = QCheckBox("Save Agro File")
        self.save_file_checkbox.setChecked(True)

        misc_layout = QHBoxLayout()
        misc_layout.addLayout(yaml_name_layout)
        misc_layout.addWidget(self.save_file_checkbox)
        misc_layout.addStretch()

        # Main
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(back_button)
        layout.addLayout(sub_layout)
        layout.addLayout(misc_layout)
        layout.addLayout(run_button_layout)
        self.setLayout(layout)

        # *************************
        #      INITIALIZATION
        # *************************
        self.load_crop_yaml_files()
        self.load_site_yaml_files()

        self.crops_dropdown.setCurrentIndex(-1)
        self.crop_varieties_dropdown.setCurrentIndex(-1)
        self.crop_end_type_dropdown.setCurrentIndex(-1)
        self.sites_dropdown.setCurrentIndex(-1)
        self.site_variations_dropdown.setCurrentIndex(-1)

        self.agro_file_inputs = {}
        self.refresh_agro_info()

        # *************************
        #        SIGNALS
        # *************************

        # Crops
        self.crops_dropdown.currentIndexChanged.connect(self.load_crop_varieties)
        self.crops_dropdown.currentIndexChanged.connect(self.refresh_agro_info)
        self.crop_varieties_dropdown.currentIndexChanged.connect(self.refresh_agro_info)
        self.crop_end_type_dropdown.currentIndexChanged.connect(self.refresh_agro_info)
        self.crop_max_duration_input.textChanged.connect(self.refresh_agro_info)
        self.crop_start_date_input.dateChanged.connect(self.refresh_agro_info)
        self.crop_end_date_input.dateChanged.connect(self.refresh_agro_info)

        # Sites
        self.sites_dropdown.currentIndexChanged.connect(self.load_site_variations)
        self.sites_dropdown.currentIndexChanged.connect(self.refresh_agro_info)
        self.site_variations_dropdown.currentIndexChanged.connect(self.refresh_agro_info)
        self.site_latitude_input.textChanged.connect(self.refresh_agro_info)
        self.site_longitude_input.textChanged.connect(self.refresh_agro_info)
        self.site_year_input.textChanged.connect(self.refresh_agro_info)
        self.site_start_date_input.dateChanged.connect(self.refresh_agro_info)
        self.site_end_date_input.dateChanged.connect(self.refresh_agro_info)

    # *************************
    #       FUNCTIONS
    # *************************
    def checkInputs(self, agro_info):
        site_info = agro_info.get("AgroManagement", {}).get("SiteCalendar", {})
        crop_info = agro_info.get("AgroManagement", {}).get("CropCalendar", {})
        for key in crop_info:
            if crop_info[key] is None or crop_info[key] == "N/A" or crop_info[key] == "":
                self.notif = Notif(f"Please fill in all fields.")
                self.notif.show()
                return False
        for key in site_info:
            if site_info[key] is None or site_info[key] == "N/A" or site_info[key] == "":
                self.notif = Notif(f"Please fill in all fields.")
                self.notif.show()
                return False
            
        if site_info.get("site_start_date") > site_info.get("site_end_date"):
            self.notif = Notif("Site start date cannot be after site end date.")
            self.notif.show()
            return False
        if crop_info.get("crop_start_date") > crop_info.get("crop_end_date"):
            self.notif = Notif("Crop start date cannot be after crop end date.")
            self.notif.show()
            return False
            
        return True

    def handle_create_agro(self, create=False):
        yaml_info = ah.createAgroYaml(agroInfo=self.agro_file_inputs, create=create)
        if not yaml_info:
            self.notif = Notif("Failed to create agro YAML file.")
            self.notif.show()
            return
        
        self.agro_man_info.clear()
        self.agro_man_info.setPlainText(yaml.dump(yaml_info["agro_yaml"], default_flow_style=False, sort_keys=False))
        return yaml_info["agro_yaml"]

    def refresh_agro_info(self):
        # Crop
        crop_name = self.crops_dropdown.currentText()
        crop_variety = self.crop_varieties_dropdown.currentText()
        crop_end_type = self.crop_end_type_dropdown.currentText()
        crop_max_duration = self.crop_max_duration_input.text()
        crop_start_date = self.crop_start_date_input.date().toPython()
        crop_end_date = self.crop_end_date_input.date().toPython()
        
        if crop_name and crop_name != "":
            self.agro_file_inputs["crop_name"] = crop_name
        if crop_variety and crop_variety != "":
            self.agro_file_inputs["crop_variety"] = crop_variety
        if crop_end_type and crop_end_type != "":
            self.agro_file_inputs["crop_end_type"] = crop_end_type
        if crop_start_date and crop_start_date != "":
            self.agro_file_inputs["crop_start_date"] = crop_start_date
        if crop_end_date and crop_end_date != "":
            self.agro_file_inputs["crop_end_date"] = crop_end_date
        if crop_max_duration and crop_max_duration != "":
            try:
                self.agro_file_inputs["max_duration"] = int(crop_max_duration)
            except ValueError:
                self.notif = Notif("Invalid crop max duration. Please enter a number.")
                self.notif.show()
                self.agro_file_inputs.pop("max_duration", None)
                self.crop_max_duration_input.clear()
                return

        # Site
        site_name = self.sites_dropdown.currentText()
        site_variation = self.site_variations_dropdown.currentText()
        site_longitude = self.site_longitude_input.text()
        site_latitude = self.site_latitude_input.text()
        site_year = self.site_year_input.text()
        site_start_date = self.site_start_date_input.date().toPython()
        site_end_date = self.site_end_date_input.date().toPython()

        if site_name and site_name != "":
            self.agro_file_inputs["site_name"] = site_name
        if site_variation and site_variation != "":
            self.agro_file_inputs["site_variation"] = site_variation
        if site_longitude and site_longitude != "":
            try:
                self.agro_file_inputs["longitude"] = float(site_longitude)
            except ValueError:
                self.notif = Notif("Invalid site longitude. Please enter a number.")
                self.notif.show()
                self.agro_file_inputs.pop("longitude", None)
                self.site_longitude_input.clear()
                return
        if site_latitude and site_latitude != "":
            try:
                self.agro_file_inputs["latitude"] = float(site_latitude)
            except ValueError:
                self.notif = Notif("Invalid site latitude. Please enter a number.")
                self.notif.show()
                self.agro_file_inputs.pop("latitude", None)
                self.site_latitude_input.clear()
                return
        if site_year and site_year != "":
            try:
                self.agro_file_inputs["year"] = int(site_year)
            except ValueError:
                self.notif = Notif("Invalid site year. Please enter a number.")
                self.notif.show()
                self.agro_file_inputs.pop("year", None)
                self.site_year_input.clear()
                return
        if site_start_date and site_start_date != "":
            self.agro_file_inputs["site_start_date"] = site_start_date
        if site_end_date and site_end_date != "":
            self.agro_file_inputs["site_end_date"] = site_end_date

        self.handle_create_agro()

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

    # Run Simulation -- Uses individual agrs for crop and site variables (Depricated)
    # def run_simulation_1(self):
    #     crop_name = self.crops_dropdown.currentText()
    #     crop_variety = self.crop_varieties_dropdown.currentText()
    #     site_name = self.sites_dropdown.currentText()
    #     site_variation = self.site_variations_dropdown.currentText()

    #     if not crop_name or not crop_variety or not site_name or not site_variation:
    #         self.notif = Notif("Please select all options.")
    #         self.notif.show()
    #         return
        
    #     print("-WOFOST- Running custom agro simulation...")
    #     print("-WOFOST- Command: python3 test_wofost.py --save-folder {} --data-file {} --env-id {} --npk.ag.crop-name {} --npk.ag.crop-variety {} --npk.ag.site-name {} --npk.ag.site-variation {}".format(
    #         self.file_selections["save_folder"],
    #         self.file_selections["data_file"],
    #         self.env_selections["env_id"],
    #         crop_name,
    #         crop_variety,
    #         site_name,
    #         site_variation
    #     ))

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

    # Run Simulation -- Uses agro file inputs to create a YAML file and run the simulation
    def run_simulation(self):
        if not self.yaml_name_input.text() or not self.yaml_name_input.text().strip():
            self.notif = Notif("Please enter a name for your custom agro file.")
            self.notif.show()
            return
        
        self.agro_file_inputs['file_name'] = self.yaml_name_input.text()
        agro_info = self.handle_create_agro(create=True)
        if not self.checkInputs(agro_info):
            return
        
        try:
            print("-WOFOST- Running custom agro simulation...")
            print("-WOFOST- Command: python3 test_wofost.py --save-folder {}/ --data-file {} --env-id {} --agro-file {}".format(
                self.file_selections["save_folder"],
                self.file_selections["data_file"],
                self.env_selections["env_id"],
                self.agro_file_inputs['file_name'] + ".yaml"
            ))
            subprocess.run([
                "python3", "test_wofost.py",
                "--save-folder", f"{self.file_selections['save_folder']}/",
                "--data-file", f"{self.file_selections['data_file']}",
                "--env-id", f"{self.env_selections['env_id']}",
                "--agro-file", f"{self.agro_file_inputs['file_name']}.yaml"
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
        if not self.yaml_name_input.text() or not self.yaml_name_input.text().strip():
            self.notif = Notif("Please enter a name for your custom agro file.")
            self.notif.show()
            return
        
        self.agro_file_inputs['file_name'] = self.yaml_name_input.text()
        agro_info = self.handle_create_agro(create=True)
        if not self.checkInputs(agro_info):
            return
        
        self.env_selections["agro_file"] = self.agro_file_inputs['file_name'] + ".yaml"
        self.train_agent_page = TrainAgentPage(
            pages=self.pages,
            env_selections=self.env_selections,
            file_selections=self.file_selections,
        )
        self.train_agent_page.show()
        self.hide()

    # Navigation
    def go_back(self):
        self.pages["agro_page"].show()
        self.close()