from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QMenu)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QIcon
from utils.session import current_session
from user_dashboard.create_booking import CreateBookingWindow
from user_dashboard.view_bookings import ViewBookingsWindow
import os

class UserDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Dashboard")
        self.setFixedSize(1000, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                color: white;
            }
            QPushButton#userButton {
                border: none;
                border-radius: 20px;
                padding: 5px;
                color: #ecf0f1;
                background-color: rgba(52, 73, 94, 0.7);
            }
            QPushButton#userButton:hover {
                background-color: rgba(52, 73, 94, 1);
            }
            QMenu {
                background-color: #34495e;
                border: 1px solid #3d566e;
                border-radius: 8px;
                padding: 8px 0px;
            }
            QMenu::item {
                padding: 8px 25px;
                color: white;
                border-radius: 4px;
                margin: 3px 6px;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d566e;
                margin: 6px 15px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with shadow effect
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                color: white;
                border-bottom: 2px solid #2c3e50;
            }
        """)
        header_widget.setFixedHeight(70)
        header_layout = QHBoxLayout(header_widget)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome back, {current_session.username}!")
        welcome_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            padding-left: 25px;
            letter-spacing: 0.5px;
        """)
        
        # User button with dropdown
        user_button = QPushButton("⏣  ﹀")
        user_button.setObjectName("userButton")
        user_button.setFixedSize(100, 40)
        user_button.setStyleSheet("""
            QPushButton#userButton {
                font-size: 18px;
                border: none;
                border-radius: 20px;
                padding: 5px;
                color: white;
                text-align: center;
            }
            QPushButton#userButton:hover {
                background-color: #34495e;
            }
        """)
        
        menu = QMenu(self)
        menu.addAction("Profile")
        menu.addSeparator()
        logout_action = menu.addAction("Logout")
        logout_action.triggered.connect(self.handle_logout)
        
        def toggle_arrow():
            current_text = user_button.text()
            if "﹀" in current_text:
                user_button.setText("⏣ ︿")
            else:
                user_button.setText("⏣ ﹀")
            menu.exec(user_button.mapToGlobal(
                QPoint(user_button.rect().right() - menu.sizeHint().width(), 
                    user_button.rect().bottom())))
            user_button.setText("⏣ ﹀")
        
        user_button.clicked.connect(toggle_arrow)

        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(user_button)
        
        layout.addWidget(header_widget)
        
        # Main content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        
        # Action buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        buttons_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create the three main buttons
        create_booking_btn = self.create_action_button("Create Booking", "booking_icon.png")
        create_booking_btn.clicked.connect(self.show_booking_form)
        
        view_bookings_btn = self.create_action_button("My Bookings", "bookings_icon.png")
        view_bookings_btn.clicked.connect(self.show_bookings)
        
        view_drivers_btn = self.create_action_button("Available Drivers", "drivers_icon.png")
        view_drivers_btn.clicked.connect(self.show_available_drivers)
        
        buttons_layout.addWidget(create_booking_btn)
        buttons_layout.addWidget(view_bookings_btn)
        buttons_layout.addWidget(view_drivers_btn)
        
        content_layout.addLayout(buttons_layout)
        layout.addWidget(content_widget)
    
    def show_booking_form(self):
        self.booking_window = CreateBookingWindow(self)
        self.booking_window.show()
    
    def show_bookings(self):
        self.bookings_window = ViewBookingsWindow(self)
        self.bookings_window.show()
    
    def show_available_drivers(self):
        from user_dashboard.view_drivers import ViewDriversWindow
        self.drivers_window = ViewDriversWindow(self)
        self.drivers_window.show()
    
    def create_action_button(self, text, icon_name):
        button = QPushButton()
        button.setFixedSize(250, 250)
        
        btn_layout = QVBoxLayout(button)
        btn_layout.setSpacing(20)
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", icon_name)
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            scaled_pixmap = icon_pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            padding: 8px;
            letter-spacing: 0.5px;
        """)
        
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(text_label)
        
        button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                border: 2px solid #2c3e50;
                border-radius: 15px;
                transition: all 0.3s;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                border: 2px solid #45a049;
                transform: translateY(-5px);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                transform: translateY(2px);
            }
        """)
        
        return button
        
    def handle_logout(self):
        from login_window import LoginWindow
        current_session.clear_session()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
