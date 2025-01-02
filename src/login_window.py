from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QLineEdit, QPushButton, QLabel, QMessageBox,
                           QHBoxLayout)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap
import sqlite3
import os
from utils.session import current_session

class IconLineEdit(QLineEdit):
    def __init__(self, icon_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_label = QLabel(icon_text, self)
        self.icon_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 18px;
                background-color: transparent;
            }
        """)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        icon_size = self.icon_label.sizeHint()
        icon_position = QPoint(10, (self.height() - icon_size.height()) // 2)
        self.icon_label.move(icon_position)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Taxi Booking System - Login")
        self.setFixedSize(400, 500)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #2c3e50;
                color: #ffffff;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create widgets
        title_label = QLabel("Taxi Booking System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: white;")

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "taxi_logo.jpg")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Input field style
        input_style = """
            QLineEdit {
                padding: 12px;
                padding-left: 40px;
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #3d566e;
                border: 2px solid #4CAF50;
            }
        """
        
        # Create custom input fields with icons
        self.email_input = IconLineEdit("📧")
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setStyleSheet(input_style)
        
        self.password_input = IconLineEdit("🔑")
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)
        
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        login_button.clicked.connect(self.handle_login)
        
        # Create Register link
        register_link = QPushButton("New user? Register here")
        register_link.setStyleSheet("""
            QPushButton {
                border: none;
                color: #4CAF50;
                text-decoration: underline;
                background: transparent;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #45a049;
            }
        """)
        register_link.clicked.connect(self.show_registration)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(logo_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(register_link)
        
        # Add some spacing
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Store registration window reference
        self.registration_window = None

    def show_registration(self):
        from register_window import RegisterWindow
        self.register_window = RegisterWindow(self)
        self.register_window.show()
        self.hide()
 
    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password!")
            return
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'taxi_booking.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check in all three tables
        tables = ['users', 'drivers', 'admins']
        user_found = False
        
        for table in tables:
            cursor.execute(f'''
                SELECT * FROM {table} 
                WHERE email = ? AND password = ?
            ''', (email, password))
            
            user = cursor.fetchone()
            if user:
                user_found = True
                user_type = table
                break
        
        conn.close()
        
        if user_found:
            # Create session with user data
            current_session.create_session(user, user_type)
            
            if user_type == 'users':
                from user_dashboard.user_main import UserDashboard
                self.user_dashboard = UserDashboard()
                self.user_dashboard.show()
            elif user_type == 'drivers':
                from driver_dashboard.driver_main import DriverDashboard
                self.driver_dashboard = DriverDashboard()
                self.driver_dashboard.show()
            elif user_type == 'admins':
                from admin_dashboard.admin_main import AdminDashboard
                self.admin_dashboard = AdminDashboard()
                self.admin_dashboard.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password!")
