import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QCoreApplication, QCommandLineParser, QCommandLineOption

class ImageGallery(QWidget):
    def __init__(self, save_folder):
        super().__init__()

        self.setWindowTitle(f"Results from {save_folder}")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        if os.path.exists(save_folder):
            plot_files = [f for f in os.listdir(save_folder) if f.lower().endswith('.png')]

            if not plot_files:
                error_label = QLabel("No plots found in the specified folder.")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                container_layout.addWidget(error_label)
            else:
                for plot_file in plot_files:
                    full_path = os.path.join(save_folder, plot_file)
                    pixmap = QPixmap(full_path)
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(699, 547, Qt.AspectRatioMode.KeepAspectRatio))
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    container_layout.addWidget(label)
        else:
            error_label = QLabel("The specified folder does not exist.")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(error_label)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    parser = QCommandLineParser()
    parser.setApplicationDescription("Display plot diagrams from a specified save folder.")
    parser.addHelpOption()

    save_folder_option = QCommandLineOption(["f", "save-folder"], "Path to the save folder.", "saves")
    parser.addOption(save_folder_option)

    parser.process(app)

    save_folder = parser.value(save_folder_option)

    if not save_folder:
        print("Error: Please specify the images folder using the --save-folder option.")
        sys.exit(1)

    window = ImageGallery(save_folder)
    window.show()
    sys.exit(app.exec())
