import sys
from envPage import EnvironmentPage
from trainAgentPage import TrainAgentPage
from notif import Notif

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import QSize

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
        header_label = QLabel("WOFOSTGym Simulation Tool")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_label.setFixedHeight(30)

        # Description
        description_label = QLabel("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                  "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ")
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 12px; color: gray;")
        description_label.setFixedHeight(40)

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
        inputs.setLayout(inputs_layout)

        # *************************
        #        BUTTONS
        # *************************
        self.gen_data_button = QPushButton("Generate Data")
        self.gen_data_button.clicked.connect(self.nav_gen_data)

        self.run_process_button = QPushButton("Run Sim/Train")
        self.run_process_button.clicked.connect(self.run_process)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.gen_data_button)
        button_layout.addWidget(self.run_process_button)

        # *************************
        #        MAIN LAYOUT
        # *************************
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(header_label)
        main_layout.addWidget(description_label)
        main_layout.addWidget(inputs)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


    # *************************
    #        FUNCTIONS
    # *************************
    def nav_gen_data(self):
        pass

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
