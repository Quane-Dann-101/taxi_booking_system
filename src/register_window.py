from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLineEdit, QPushButton, QLabel, QMessageBox,
                           QRadioButton, QButtonGroup, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QRegularExpressionValidator, QColor
import sqlite3
import os
import re

class RegisterWindow(QMainWindow):
    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Taxi Booking System - Registration")
        self.setFixedSize(800, 600)

        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #2c3e50;
                color: #ffffff;
            }
            QRadioButton {
                color: #ffffff;
            }
            QLineEdit {
                padding-left: 30px;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header Section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "taxi_logo.jpg")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel("New User Registration")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: white;")
        
        # Back link at the top
        back_link = QPushButton("← Back to Login")
        back_link.setStyleSheet("""
            QPushButton {
                border: none;
                color: #4CAF50;
                text-decoration: underline;
                background: transparent;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                color: #45a049;
            }
        """)
        back_link.clicked.connect(self.back_to_login)
        
        # User type selection
        user_type_layout = QHBoxLayout()
        user_type_label = QLabel("Register as:")
        user_type_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.user_radio = QRadioButton("User")
        self.driver_radio = QRadioButton("Driver")
        self.user_radio.setChecked(True)
        
        self.user_radio_group = QButtonGroup()
        self.user_radio_group.addButton(self.user_radio)
        self.user_radio_group.addButton(self.driver_radio)
        
        user_type_layout.addWidget(user_type_label)
        user_type_layout.addWidget(self.user_radio)
        user_type_layout.addWidget(self.driver_radio)
        user_type_layout.addStretch()
        
        header_layout.addWidget(back_link, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addLayout(user_type_layout)
        
        # Create a fixed-height container for form fields
        form_container = QFrame()
        form_container.setFrameStyle(QFrame.Shape.StyledPanel)
        form_container.setFixedHeight(250)
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                border: 1px solid #3d566e;
            }
        """)

        # Input field style
        input_style = """
            QLineEdit {
                padding: 12px;
                padding-left: 35px;
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                background-repeat: no-repeat;
                background-position: left center;
                background-origin: content;
            }
            QLineEdit:focus {
                background-color: #3d566e;
                border: 2px solid #4CAF50;
            }
        """
        
        # Initialize form fields with icons
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/user.png);
                padding-left: 35px;
            }
        """)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/lock.png);
                padding-left: 35px;
            }
        """)
        
        # Password strength indicator
        self.strength_label = QLabel()
        self.strength_label.setStyleSheet("font-size: 12px;")
        
        def update_password_strength():
            password = self.password.text()
            if password:
                strength, color, feedback = self.check_password_strength(password)
                self.strength_label.setText(f"Password Strength: {strength}")
                self.strength_label.setStyleSheet(f"color: {color}; font-size: 12px;")
                self.password.setToolTip("\n".join(feedback))
            else:
                self.strength_label.setText("")
        
        self.password.textChanged.connect(update_password_strength)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/lock.png);
                padding-left: 35px;
            }
        """)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/email.png);
                padding-left: 35px;
            }
        """)
        
        self.phone = QLineEdit()
        self.phone.setInputMask("(868) 000-0000")
        self.phone.setText("(868) ")
        self.phone.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/phone.png);
                padding-left: 35px;
            }
        """)
        
        def phone_changed():
            if not self.phone.text().startswith("(868) "):
                self.phone.setText("(868) " + self.phone.text().replace("(868) ", ""))
        
        self.phone.textChanged.connect(phone_changed)
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Address")
        self.address.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/address.png);
                padding-left: 35px;
            }
        """)
        
        self.car_model = QLineEdit()
        self.car_model.setPlaceholderText("Car Model")
        self.car_model.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/car.png);
                padding-left: 35px;
            }
        """)
        
        self.license_plate = QLineEdit()
        self.license_plate.setPlaceholderText("License Plate")
        self.license_plate.setStyleSheet(input_style + """
            QLineEdit {
                background-image: url(resources/license.png);
                padding-left: 35px;
            }
        """)
        
        # Create grid layout for form fields inside container
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add fields to grid
        form_layout.addWidget(self.username, 0, 0)
        form_layout.addWidget(self.password, 0, 1)
        form_layout.addWidget(self.strength_label, 0, 3)
        form_layout.addWidget(self.confirm_password, 0, 2)
        form_layout.addWidget(self.email, 1, 0)
        form_layout.addWidget(self.phone, 1, 1)
        form_layout.addWidget(self.address, 1, 2)
        form_layout.addWidget(self.car_model, 2, 0)
        form_layout.addWidget(self.license_plate, 2, 1)
        
        # Register button
        register_button = QPushButton("Register")
        register_button.setStyleSheet("""
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
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(register_button)
        
        # Add all components to main layout
        layout.addWidget(header_widget)
        layout.addWidget(form_container)
        layout.addLayout(button_layout)
        
        # Set layout properties
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Connect signals
        register_button.clicked.connect(self.handle_registration)
        self.user_radio_group.buttonClicked.connect(self.toggle_driver_fields)
        
        # Initially hide driver fields
        self.toggle_driver_fields(self.user_radio)

    def check_password_strength(self, password):
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters")
            
        # Check for numbers
        if any(char.isdigit() for char in password):
            score += 1
        else:
            feedback.append("Include at least one number")
            
        # Check for uppercase
        if any(char.isupper() for char in password):
            score += 1
        else:
            feedback.append("Include at least one uppercase letter")
            
        # Check for lowercase
        if any(char.islower() for char in password):
            score += 1
        else:
            feedback.append("Include at least one lowercase letter")
            
        # Check for special characters
        if any(not char.isalnum() for char in password):
            score += 1
        else:
            feedback.append("Include at least one special character")
        
        # Determine strength level
        if score < 2:
            return "Weak", "#ff4444", feedback
        elif score < 4:
            return "Medium", "#ffbb33", feedback
        else:
            return "Strong", "#00C851", feedback

    def toggle_driver_fields(self, button):
        is_driver = button == self.driver_radio
        self.car_model.setVisible(is_driver)
        self.license_plate.setVisible(is_driver)

    def validate_input(self):
        # Check password strength first
        strength, _, _ = self.check_password_strength(self.password.text())
        if strength == "Weak":
            QMessageBox.warning(self, "Error", "Password is too weak! Please create a stronger password.")
            return False
            
        # Check minimum length for all fields
        if any(len(field.text()) < 5 for field in [self.username, self.password, self.email]):
            QMessageBox.warning(self, "Error", "Username, password, and email must contain at least 5 characters!")
            return False
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email.text()):
            QMessageBox.warning(self, "Error", "Please enter a valid email address!")
            return False
        
        try:
            # Check if email or phone already exists across all tables
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'taxi_booking.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, phone FROM users 
                WHERE email = ? OR phone = ?
                UNION
                SELECT email, phone FROM drivers 
                WHERE email = ? OR phone = ?
                UNION
                SELECT email, phone FROM admins 
                WHERE email = ? OR phone = ?
            ''', (self.email.text(), self.phone.text(), self.email.text(), self.phone.text(), 
                  self.email.text(), self.phone.text()))
            
            result = cursor.fetchone()
            if result:
                if result[0] == self.email.text():
                    QMessageBox.warning(self, "Error", "This email is already registered!")
                else:
                    QMessageBox.warning(self, "Error", "This phone number is already registered!")
                return False
            
            # Validate phone number format
            if not self.phone.text().startswith("(868) ") or len(self.phone.text()) != 14:
                QMessageBox.warning(self, "Error", "Phone number must be in format: (868) xxx-xxxx")
                return False
            
            # Validate password match
            if self.password.text() != self.confirm_password.text():
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return False
            
            # Check required fields
            if not all([self.username.text(), self.password.text(), self.email.text(), 
                       self.phone.text()]):
                QMessageBox.warning(self, "Error", "Please fill in all required fields!")
                return False
            
            # Check driver-specific fields
            if self.driver_radio.isChecked() and not all([self.car_model.text(), 
                                                         self.license_plate.text()]):
                QMessageBox.warning(self, "Error", "Please fill in all driver details!")
                return False
            
            return True
            
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_registration(self):
        if not self.validate_input():
            return
        
        user_type = "driver" if self.driver_radio.isChecked() else "user"
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'taxi_booking.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            if user_type == "user":
                cursor.execute('''
                    INSERT INTO users (username, password, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.username.text(), self.password.text(), self.email.text(),
                     self.phone.text(), self.address.text()))
            else:
                cursor.execute('''
                    INSERT INTO drivers (username, password, email, phone, car_model, 
                    license_plate, full_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.username.text(), self.password.text(), self.email.text(),
                     self.phone.text(), self.car_model.text(), self.license_plate.text(),
                     self.username.text()))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Registration successful!")
            self.back_to_login()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists!")
        finally:
            conn.close()

    def back_to_login(self):
        if self.login_window:
            self.login_window.show()
        self.close()

