from agroPage import AgromanagementPage
from notif import Notif

from PySide6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QCheckBox,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import QSize, Qt

class EnvironmentPage(QWidget):
    def __init__(self, home_page, file_selections):
        super().__init__()
        self.setWindowTitle("Environment Setup")
        self.setFixedSize(400, 400)
        self.file_selections = file_selections
        self.home_page = home_page

        # *************************
        #        VARIABLES
        # *************************
        vars = QGroupBox("")
        vars_layout = QVBoxLayout()
        vars_layout.setContentsMargins(10, 10, 10, 10)
        vars_layout.setSpacing(10)

        # ===== VARIABLE 1 : Cycle =====
        self.env_var1_label = QLabel("Cycle:")
        self.env_var1_label.setFixedSize(QSize(100, 30))
        self.env_var1_dropdown = QComboBox()
        self.env_var1_dropdown.addItems([
            "Annual",
            "Perennial",
            "Grape Specific",
            "Annual - Multi Farm",
            "Perennial - Multi Farm",
        ])
        self.env_var1_dropdown.setCurrentIndex(-1)
        self.env_var1_dropdown.setFixedSize(QSize(200, 30))
        self.env_var1_dropdown.currentIndexChanged.connect(self.var_1_change)

        self.env_var1_label2 = QLabel("- Crop Options:")
        self.env_var1_label2.setFixedSize(QSize(300, 30))

        env_var1_row = QHBoxLayout()
        env_var1_row.addWidget(self.env_var1_label)
        env_var1_row.addWidget(self.env_var1_dropdown)
        env_var1_row.addStretch()

        env_var1_layout = QVBoxLayout()
        env_var1_layout.addLayout(env_var1_row)
        env_var1_layout.addWidget(self.env_var1_label2)

        # V===== VARIABLE 2 : Type =====
        self.env_var2_label = QLabel("Type:")
        self.env_var2_label.setFixedSize(QSize(100, 30))

        self.env_var2_dropdown = QComboBox()
        self.env_var2_dropdown.setFixedSize(QSize(200, 30))
        self.env_var2_dropdown.setCurrentIndex(-1)

        env_var2_layout = QHBoxLayout()
        env_var2_layout.addWidget(self.env_var2_label)
        env_var2_layout.addWidget(self.env_var2_dropdown)
        env_var2_layout.addStretch()

        # ===== VARIABLE 3 : Limitations =====
        self.env_var3_label = QLabel("Limitations:")
        self.env_var3_label.setFixedSize(QSize(100, 30))

        self.env_var3_dropdown = QComboBox()
        self.env_var3_dropdown.setFixedSize(QSize(200, 30))

        self.env_var3_checkbox = QCheckBox("Layered")
        self.env_var3_checkbox.setChecked(False)
        self.env_var3_checkbox.stateChanged.connect(self.layered_check)

        env_var3_inner_layout = QHBoxLayout()
        env_var3_inner_layout.addWidget(self.env_var3_label)
        env_var3_inner_layout.addWidget(self.env_var3_dropdown)
        env_var3_inner_layout.addStretch()

        env_var3_layout = QVBoxLayout()
        env_var3_layout.addLayout(env_var3_inner_layout)
        env_var3_layout.addWidget(self.env_var3_checkbox)

        # **************************
        #        BUTTONS
        # **************************
        # ===== BACK =====
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        # ===== CONTINUE =====
        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.go_next)

        # **************************
        #        MAIN LAYOUT
        # **************************
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        vars_layout.addLayout(env_var1_layout)
        vars_layout.addLayout(env_var2_layout)
        vars_layout.addLayout(env_var3_layout)
        vars.setLayout(vars_layout)

        layout.addWidget(back_button)
        layout.addWidget(vars)
        layout.addWidget(continue_button)
        self.setLayout(layout)

    # **************************
    #        FUNCTIONS
    # **************************
    def var_1_change(self):
        var_1 = self.env_var1_dropdown.currentText()

        if var_1 == "Annual":
            self.env_var1_label2.setText("- Crop Options: All except grape, jujube, and pear")
            var2_options = ["Default", "Harvesting", "Planting"]
        elif var_1 == "Perennial":
            self.env_var1_label2.setText("- Crop Options: Only Jujube and Pear")
            var2_options = ["Default", "Harvesting", "Planting"]
        elif var_1 == "Grape Specific":
            self.env_var1_label2.setText("- Crop Options: Only Grape")
            var2_options = ["Default"]
        elif var_1 == "Annual - Multi Farm":
            self.env_var1_label2.setText("- Crop Options: All except grape, jujube, and pear")
            var2_options = ["Default"]
        elif var_1 == "Perennial - Multi Farm":
            self.env_var1_label2.setText("- Crop Options: Only Jujube and Pear")
            var2_options = []
        else:
            self.env_var1_label2.setText("- Crop Options:")
            var2_options = []

        self.env_var2_dropdown.clear()
        self.env_var2_dropdown.addItems(var2_options)
        self.env_var2_dropdown.setCurrentIndex(-1)
        self.layered_check()

    def layered_check(self):
        current_var1 = self.env_var1_dropdown.currentText()
        layered = self.env_var3_checkbox.isChecked()

        if current_var1 == "Perennial - Multi Farm":
            var3_options = []
        else:
            if layered:
                var3_options = ["llnpkw", "lpp", "llnpk", "lln", "llnw", "llw"]
            else:
                var3_options = ["lnpkw", "pp", "lnpk", "ln", "lnw", "lw"]

        self.env_var3_dropdown.clear()
        self.env_var3_dropdown.addItems(var3_options)
        self.env_var3_dropdown.setCurrentIndex(-1)

    def go_back(self):
        self.home_page.show()
        self.close()


    def go_next(self):
        env_selections = {
            "cycle": self.env_var1_dropdown.currentText(),
            "type": self.env_var2_dropdown.currentText(),
            "limitations": self.env_var3_dropdown.currentText(),
        }


        if env_selections["cycle"] == "" or env_selections["type"] == "" or env_selections["limitations"] == "":
            self.notif = Notif("Please select all options.")
            self.notif.show()
            return

        self.aggro_page = AgromanagementPage(env_page=self, env_selections=env_selections, file_selections=self.file_selections)
        self.aggro_page.show()
        self.hide()
