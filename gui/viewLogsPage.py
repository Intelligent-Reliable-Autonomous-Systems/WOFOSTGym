import os
import webbrowser
import subprocess
import time
from notif import Notif

from PySide6.QtWidgets import (
    QWidget, QPushButton,
    QVBoxLayout, QLabel, QComboBox
)
from PySide6.QtCore import QSize

POSSIBLE_AGENT_TYPES = ["PPO", "SAC", "DQN", "GAIL", "AIRL", "BC"]

class ViewLogsPage(QWidget):
    def __init__(self, pages, file_selections):
        super().__init__()
        self.setWindowTitle("TensorBoard Log Viewer")
        self.setFixedSize(400, 400)
        self.pages = pages
        self.pages["view_logs_page"] = self
        self.file_selections = file_selections

        self.logs = {}
        self.tb_proc = None
        self.load_training_files()

        # *************************
        #        VARIABLES
        # *************************
        self.label = QLabel("Showing logs stored in save_folder: " + self.file_selections["save_folder"])
        self.label.setFixedSize(QSize(350, 30))

        self.agent_type_dropdown = QComboBox()
        for agent in self.logs.keys():
            self.agent_type_dropdown.addItem(agent)
        self.agent_type_dropdown.setCurrentIndex(-1)
        self.agent_type_dropdown.currentIndexChanged.connect(self.update_log_dropdown)

        self.log_dropdown = QComboBox()
        # self.log_dropdown.setFixedSize(QSize(200, 30))

        # *************************
        #         BUTTONS
        # *************************

        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        self.open_tb = QPushButton("Open TensorBoard")
        self.open_tb.setFixedSize(QSize(125, 30))
        self.open_tb.clicked.connect(self.open_tensorboard)

        # *************************
        #        MAIN LAYOUT
        # *************************

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(back_button)
        layout.addWidget(self.label)
        layout.addWidget(self.agent_type_dropdown)
        layout.addWidget(self.log_dropdown)
        layout.addWidget(self.open_tb)
        self.setLayout(layout)


    # *************************
    #        FUNCTIONS
    # *************************
    def update_log_dropdown(self):
        self.log_dropdown.clear()
        selected_agent = self.agent_type_dropdown.currentText()
        if selected_agent in self.logs:
            for log in self.logs[selected_agent]:
                self.log_dropdown.addItem(log)
        else:
            print(f"-WOFOST- No logs found for agent type: {selected_agent}")

        self.log_dropdown.setCurrentIndex(-1)

    def load_training_files(self):
        save_path = self.file_selections["save_folder"]
        
        for agent_type in POSSIBLE_AGENT_TYPES:
            agent_path = os.path.join(save_path, agent_type)
            if not os.path.isdir(agent_path):
                # print(f"-WOFOST- No logs found for agent type: {agent_type}")
                continue
            else:
                self.logs[agent_type] = [log for log in os.listdir(agent_path)]

    def open_tensorboard(self):
        if self.agent_type_dropdown.currentIndex() == -1 or self.log_dropdown.currentIndex() == -1:
            self.notif = Notif("Please select an agent type and a log.")
            self.notif.show()
            return

        if self.tb_proc and self.tb_proc.poll() is None:
            self.tb_proc.terminate()
            print("-WOFOST- Previous TensorBoard process terminated.")

        logdir = os.path.join(self.file_selections["save_folder"], 
                                self.agent_type_dropdown.currentText(), 
                                self.log_dropdown.currentText())

        self.tb_proc = subprocess.Popen(
            ["tensorboard", f"--logdir={logdir}"],
        )
        print("-WOFOST- TensorBoard started with logdir:", logdir)
        print("-WOFOST- Command: tensorboard --logdir={}".format(logdir))
        time.sleep(1)
        webbrowser.open(f"http://localhost:6006")


    def closeEvent(self, event):
        if self.tb_proc and self.tb_proc.poll() is None:
            self.tb_proc.terminate()
            print("-WOFOST- TensorBoard process terminated.")

        event.accept()

    # ===== NAVIGATION =====
    def go_back(self):
        self.pages["train_agent_page"].show()
        self.close()
            
            