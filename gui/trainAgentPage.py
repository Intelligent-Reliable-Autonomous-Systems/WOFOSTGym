import os
import webbrowser
import subprocess
from notif import Notif

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QProgressBar,
    QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QComboBox
)
from PySide6.QtCore import QSize, QTimer, Qt

def get_latest_logdir(base_dir):
    try:
        entries = os.listdir(base_dir)
        subdirs = [os.path.join(base_dir, d) for d in entries if os.path.isdir(os.path.join(base_dir, d))]
        if not subdirs:
            return None
        latest_dir = max(subdirs, key=os.path.getmtime)
        return latest_dir
    except FileNotFoundError:
        return None

class TrainingPage(QWidget):
    def __init__(self, home_page, file_selections, agent_type):
        super().__init__()
        self.setWindowTitle("Training Controller")
        self.setFixedSize(400, 100)
        self.agent_type = agent_type
        self.home_page = home_page
        self.file_selections = file_selections

        self.label = QLabel("Training in progress...")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        
        # *************************
        #        BUTTONS
        # *************************
        # Terminate Training
        self.stop_button = QPushButton("Stop Training")
        self.stop_button.setFixedSize(QSize(100, 30))
        self.stop_button.clicked.connect(self.stop_training)

        # Open TensorBoard
        self.open_tb = QPushButton("Open TensorBoard")
        self.open_tb.setFixedSize(QSize(125, 30))
        self.open_tb.clicked.connect(self.open_tensorboard)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.open_tb)
        button_layout.addStretch()

        # *************************
        #       MAIN LAYOUT
        # *************************
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.train_proc = subprocess.Popen(
            ["python", "train_agent.py", "--agent_type", self.agent_type,
             "--save-folder", self.file_selections["save_folder"] + "/"],
        )

        print("-WOFOST- Command: python train_agent.py --agent_type {} --save-folder {}".format(
            self.agent_type, self.file_selections["save_folder"] + "/"
        ))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_training_status)
        self.timer.start(1000) 

        self.tb_proc = None

    # *************************
    #       MAIN LAYOUT
    # *************************

    def check_training_status(self):
        if self.train_proc and self.train_proc.poll() is not None:
            exit_code = self.train_proc.returncode
            self.timer.stop()
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(1)

            if exit_code == 0:
                self.notif = Notif("Training completed successfully.")
                self.notif.show()
                print("-WOFOST- Training completed successfully.")
            else:
                self.notif = Notif(f"Training exited with error (code {exit_code}).")
                self.notif.show()
                print(f"-WOFOST- Training exited with error (code {exit_code}).")


            if self.tb_proc and self.tb_proc.poll() is None:
                self.tb_proc.terminate()
                print("-WOFOST- TensorBoard process terminated.")

            self.home_page.show()
            self.close()

    def stop_training(self):
        if self.tb_proc and self.tb_proc.poll() is None:
            self.tb_proc.terminate()
            print("-WOFOST- TensorBoard process terminated.")
        if self.train_proc and self.train_proc.poll() is None:
            self.train_proc.terminate()
            self.notif = Notif("Training terminated by user.")
            self.notif.show()
            print("-WOFOST- Training process terminated by user.")
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.timer.stop()
        self.home_page.show()
        self.close()

    def open_tensorboard(self):
        if self.tb_proc is None or self.tb_proc.poll() is not None:
            logdir = get_latest_logdir(self.file_selections["save_folder"] + f"/{self.agent_type}/")
            if logdir is None:
                self.notif = Notif("No TensorBoard logs found. Please ensure training has been run.")
                self.notif.show()
                return
            
            self.tb_proc = subprocess.Popen(
                ["tensorboard", f"--logdir={logdir}"],
            )
            print("-WOFOST- TensorBoard started with logdir:", logdir)
            print("-WOFOST- Command: tensorboard --logdir={}".format(logdir))
            webbrowser.open(f"http://localhost:6006")
        else:
            self.notif = Notif("TensorBoard is already running.")
            self.notif.show()
            webbrowser.open(f"http://localhost:6006")

    def closeEvent(self, event):
        if self.tb_proc and self.tb_proc.poll() is None:
            self.tb_proc.terminate()
            print("-WOFOST- TensorBoard process terminated in closeEvent.")

        if self.train_proc and self.train_proc.poll() is None:
            self.train_proc.terminate()
            print("-WOFOST- Training process terminated in closeEvent.")

        if self.timer.isActive():
            self.timer.stop()

        event.accept()


class TrainAgentPage(QWidget):
    def __init__(self, home_page, file_selections):
        super().__init__()
        self.setWindowTitle("Train Agent")
        self.setFixedSize(400, 400)
        self.file_selections = file_selections
        self.home_page = home_page

        # *************************
        #        VARIABLES
        # *************************
        types = QGroupBox("")
        types_layout = QVBoxLayout()

        # ===== AGENT TYPE =====
        self.types_label = QLabel("Agent Type:")
        self.types_label.setFixedSize(QSize(100, 30))
        self.types_dropdown = QComboBox()
        self.types_dropdown.addItems([
            "PPO", "SAC", "DQN", "GAIL", "AIRL", "BC"
        ])
        self.types_dropdown.setCurrentIndex(-1)

        types_layout = QHBoxLayout()
        types_layout.addWidget(self.types_label)
        types_layout.addWidget(self.types_dropdown)
        types_layout.addStretch()

        types.setLayout(types_layout)

        # *************************
        #         BUTTONS
        # *************************
        back_button = QPushButton("Back")
        back_button.setFixedSize(QSize(50, 30))
        back_button.clicked.connect(self.go_back)

        train_button = QPushButton("Start Training")
        train_button.clicked.connect(self.start_training)

        # *************************
        #       MAIN LAYOUT
        # *************************
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        layout.addWidget(back_button)
        layout.addWidget(types)
        layout.addWidget(train_button)
        self.setLayout(layout)

    # *************************
    #       FUNCTIONS
    # *************************

    # ===== START TRAINING =====
    def start_training(self):
        if self.types_dropdown.currentIndex() == -1:
            self.notif = Notif("Please select an agent type.")
            self.notif.show()
            return
        
        print("-WOFOST- Training started with agent type:", self.types_dropdown.currentText())

        self.training_page = TrainingPage(home_page=self.home_page, file_selections=self.file_selections,
                                          agent_type=self.types_dropdown.currentText())
        
        self.training_page.show()
        self.close()

    # ===== NAVIGATION =====
    def go_back(self):
        self.home_page.show()
        self.close()