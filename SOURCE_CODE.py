import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image

class PixelMakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pixelMaker")
        
        # Set minimum and default window size
        self.setMinimumSize(850, 620)
        self.resize(850, 620)
        
        # Remove standard Windows border
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Variables for window dragging & fullscreen status
        self.drag_position = QPoint()
        self.is_fullscreen = False

        self.original_image = None
        self.processed_image = None

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Global Dark Theme Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                border: 1px solid #3F3F3F;
            }
            QWidget {
                color: #E0E0E0;
                font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                font-size: 14px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3F3F3F;
                height: 6px;
                background: #2D2D2D;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #007AFF;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)

        self.create_welcome_page()
        self.create_editor_page()
        self.stacked_widget.setCurrentIndex(0)

    # --- PERFECT ROUND MACOS TITEL BAR BUTTONS ---
    def create_custom_title_bar(self, include_back_button=False):
        """Creates the macOS title bar with perfectly round buttons"""
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(15, 12, 15, 12)

        # Container widget for the three dots
        dot_container = QWidget()
        dot_layout = QHBoxLayout(dot_container)
        dot_layout.setContentsMargins(0, 0, 0, 0)
        dot_layout.setSpacing(8) 

        # CSS to enforce perfect unstretchable circles
        circle_style = """
            QPushButton {{
                background-color: {0};
                border: none;
                border-radius: 7px;
                min-width: 14px;
                max-width: 14px;
                min-height: 14px;
                max-height: 14px;
                width: 14px;
                height: 14px;
            }}
        """

        # Red = Close
        btn_close = QPushButton()
        btn_close.setStyleSheet(circle_style.format("#FF5F56"))
        btn_close.clicked.connect(self.close)
        
        # Yellow = Minimize
        btn_minimize = QPushButton()
        btn_minimize.setStyleSheet(circle_style.format("#FFBD2E"))
        btn_minimize.clicked.connect(self.showMinimized)
        
        # Green = Fullscreen
        btn_maximize = QPushButton()
        btn_maximize.setStyleSheet(circle_style.format("#27C93F"))
        btn_maximize.clicked.connect(self.toggle_fullscreen)

        dot_layout.addWidget(btn_close)
        dot_layout.addWidget(btn_minimize)
        dot_layout.addWidget(btn_maximize)
        
        title_bar_layout.addWidget(dot_container, alignment=Qt.AlignmentFlag.AlignLeft)

        # Center App Name
        title_label = QLabel("pixelMaker")
        title_label.setStyleSheet("font-size: 12px; color: #666666; font-weight: bold;")
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        # Right Area for symmetry (Back button or spacer)
        btn_normal_style = """
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3F3F3F;
                border-radius: 8px;
                padding: 4px 10px;
                min-width: 60px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #3A3A3A; border-color: #007AFF; }
        """

        if include_back_button:
            btn_back = QPushButton("← Back")
            btn_back.setStyleSheet(btn_normal_style)
            btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            title_bar_layout.addWidget(btn_back)
        else:
            spacer = QWidget()
            spacer.setFixedSize(60, 14)
            title_bar_layout.addWidget(spacer)

        return title_bar

    # --- FULLSCREEN LOGIC ---
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showMaximized()
            self.is_fullscreen = True
        
        if self.original_image:
            self.pixelate_image()

    # --- WINDOW DRAGGING LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_fullscreen:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.is_fullscreen:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # --- PAGE 1: WELCOME ---
    def create_welcome_page(self):
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        layout.setContentsMargins(0, 0, 0, 40)

        layout.addWidget(self.create_custom_title_bar(include_back_button=False))
        layout.addSpacing(60)

        title = QLabel("Welcome to pixelMaker")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #FFFFFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "This tool transforms your standard photos into stylish retro pixel art.\n\n"
            "1. Click 'Get Started'\n"
            "2. Upload any image of your choice\n"
            "3. Use the slider to control the pixelation intensity\n"
            "4. Save your pixel masterpiece!"
        )
        desc.setStyleSheet("color: #A0A0A0; line-height: 180%; font-size: 15px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch()

        btn_start = QPushButton("Get Started →")
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #007AFF; 
                color: white; 
                font-weight: bold; 
                font-size: 16px;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #1485FF; }
        """)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(btn_start)
        btn_container.addStretch()
        layout.addLayout(btn_container)

        self.stacked_widget.addWidget(welcome_widget)

    # --- PAGE 2: EDITOR ---
    def create_editor_page(self):
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        layout.setContentsMargins(0, 0, 0, 20)

        layout.addWidget(self.create_custom_title_bar(include_back_button=True))

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 0, 20, 0)

        self.image_label = QLabel("Click 'Load Image' below", self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #3F3F3F; 
                border-radius: 12px; 
                background-color: #151515;
                color: #666666;
            }
        """)
        content_layout.addWidget(self.image_label, stretch=1)
        content_layout.addSpacing(15)

        controls = QHBoxLayout()
        
        btn_style = """
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3F3F3F;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #3A3A3A; border-color: #007AFF; }
        """

        self.btn_load = QPushButton("Load Image")
        self.btn_load.setStyleSheet(btn_style)
        self.btn_load.clicked.connect(self.load_image)
        controls.addWidget(self.btn_load)

        self.slider_label = QLabel("Pixel Size: 1")
        self.slider_label.setStyleSheet("color: #A0A0A0; min-width: 100px;")
        controls.addWidget(self.slider_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 60)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.pixelate_image)
        controls.addWidget(self.slider)

        self.btn_save = QPushButton("Save Image")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #34C759; 
                color: white; 
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #28a745; }
        """) 
        self.btn_save.clicked.connect(self.save_image)
        controls.addWidget(self.btn_save)

        content_layout.addLayout(controls)
        layout.addLayout(content_layout)
        
        self.stacked_widget.addWidget(editor_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.original_image and self.processed_image:
            self.display_image(self.processed_image)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.original_image = Image.open(file_path)
            self.slider.setValue(1)
            self.display_image(self.original_image)

    def pixelate_image(self):
        if not self.original_image:
            return

        pixel_size = self.slider.value()
        self.slider_label.setText(f"Pixel Size: {pixel_size}")

        if pixel_size == 1:
            self.processed_image = self.original_image.copy()
        else:
            orig_width, orig_height = self.original_image.size
            small_width = max(1, orig_width // pixel_size)
            small_height = max(1, orig_height // pixel_size)

            img_small = self.original_image.resize((small_width, small_height), resample=Image.Resampling.BILINEAR)
            self.processed_image = img_small.resize((orig_width, orig_height), resample=Image.Resampling.NEAREST)

        self.display_image(self.processed_image)

    def display_image(self, pil_img):
        pil_img_rgb = pil_img.convert("RGBA")
        data = pil_img_rgb.tobytes("raw", "RGBA")
        qim = QImage(data, pil_img_rgb.size[0], pil_img_rgb.size[1], QImage.Format.Format_RGBA8888)
        
        pixmap = QPixmap.fromImage(qim)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def save_image(self):
        if not self.processed_image:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png);;JPEG Image (*.jpg)")
        if file_path:
            self.processed_image.save(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixelMakerApp()
    window.show()
    sys.exit(app.exec())
