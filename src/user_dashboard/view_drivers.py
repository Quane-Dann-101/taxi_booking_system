from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QScrollArea, QFrame,
                           QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QIcon
from utils.session import current_session
import sqlite3
import os

class StatusIndicator(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        
        colors = {
            'confirmed': '#27ae60',
            'on_the_way': '#2980b9'
        }
        
        color = colors.get(status.lower(), '#95a5a6')
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 2px solid white;
            }}
        """)

class DriverCard(QFrame):
    def __init__(self, driver_data, parent=None):
        super().__init__(parent)
        self.driver_data = driver_data
        self.setFixedHeight(180)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("driverCard")
        self.setStyleSheet("""
            QFrame#driverCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2C3E50, stop:1 #3498DB);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QLabel {
                color: white;
            }
            QLabel#nameLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ECF0F1;
            }
            QLabel#infoLabel {
                color: #BDC3C7;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: white;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(20)
        
        # Left section - Driver Info
        left_section = QVBoxLayout()
        
        # Driver name and status
        name_layout = QHBoxLayout()
        name_label = QLabel(self.driver_data['full_name'])
        name_label.setObjectName("nameLabel")
        status = StatusIndicator(self.driver_data['status'])
        name_layout.addWidget(name_label)
        name_layout.addWidget(status)
        name_layout.addStretch()
        
        # Vehicle info with icons
        car_info = QLabel(f"🚗 {self.driver_data['car_model']}")
        car_info.setObjectName("infoLabel")
        plate_info = QLabel(f"🔢 {self.driver_data['license_plate']}")
        plate_info.setObjectName("infoLabel")
        
        left_section.addLayout(name_layout)
        left_section.addWidget(car_info)
        left_section.addWidget(plate_info)
        left_section.addStretch()
        
        # Right section - Trip Info & Actions
        right_section = QVBoxLayout()
        
        # Trip status
        status_label = QLabel(f"Status: {self.driver_data['status'].replace('_', ' ').title()}")
        status_label.setStyleSheet("""
            color: #3498DB;
            font-weight: bold;
            font-size: 14px;
            padding: 5px 10px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 5px;
        """)
        
        # Contact info
        contact_layout = QHBoxLayout()
        phone_btn = QPushButton("📞 Call Driver")
        email_btn = QPushButton("✉️ Message")
        
        contact_layout.addWidget(phone_btn)
        contact_layout.addWidget(email_btn)
        
        right_section.addWidget(status_label)
        right_section.addStretch()
        right_section.addLayout(contact_layout)
        
        # Add sections to main layout
        main_layout.addLayout(left_section, stretch=2)
        main_layout.addLayout(right_section, stretch=1)


class ViewDriversWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Available Drivers")
        self.setFixedSize(1000, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A1A2E, stop:1 #16213E);
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2C3E50;
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #3498DB;
                border-radius: 4px;
                min-height: 30px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Header Section
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(52, 152, 219, 0.2);
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("🚖")
        icon_label.setStyleSheet("font-size: 24px;")
        self.title_label = QLabel("My Active Drivers")
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ECF0F1;
        """)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(self.title_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Drivers Grid Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        self.grid_layout = QVBoxLayout(scroll_content)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        layout.addWidget(header_widget)
        layout.addWidget(scroll_area)
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_drivers)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
        
        # Initial load
        self.refresh_drivers()
        
    def refresh_drivers(self):
        # Clear existing cards
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        try:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'database', 'taxi_booking.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    d.id,
                    d.full_name,
                    d.car_model,
                    d.license_plate,
                    d.phone,
                    d.email,
                    b.booking_status,
                    b.pickup_location,
                    b.dropoff_location
                FROM bookings b
                JOIN drivers d ON b.driver_id = d.id
                WHERE b.user_id = ?
                AND b.booking_status IN ('confirmed', 'on_the_way')
                ORDER BY b.pickup_time DESC
            ''', (current_session.user_id,))
            
            active_drivers = cursor.fetchall()
            
            if not active_drivers:
                self.show_empty_state()
            else:
                self.title_label.setText(f"My Active Drivers ({len(active_drivers)})")
                self.display_driver_cards(active_drivers)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.show_error_state(str(e))

    def show_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("🚖")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QLabel("No Active Drivers")
        message_label.setStyleSheet("""
            color: #BDC3C7;
            font-size: 18px;
            font-weight: bold;
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_message = QLabel("Drivers will appear here when they accept your bookings")
        sub_message.setStyleSheet("""
            color: #7F8C8D;
            font-size: 14px;
        """)
        sub_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(message_label)
        empty_layout.addWidget(sub_message)
        
        self.grid_layout.addWidget(empty_widget)

    def show_error_state(self, error_message):
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_label = QLabel("Unable to load drivers")
        error_label.setStyleSheet("""
            color: #E74C3C;
            font-size: 18px;
            font-weight: bold;
        """)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        retry_button = QPushButton("Retry")
        retry_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        retry_button.clicked.connect(self.refresh_drivers)
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(error_label)
        error_layout.addWidget(retry_button)
        
        self.grid_layout.addWidget(error_widget)

    def display_driver_cards(self, drivers):
        for driver in drivers:
            driver_data = {
                'id': driver[0],
                'full_name': driver[1],
                'car_model': driver[2],
                'license_plate': driver[3],
                'phone': driver[4],
                'email': driver[5],
                'status': driver[6],
                'pickup': driver[7],
                'dropoff': driver[8]
            }
            
            card = DriverCard(driver_data)
            self.grid_layout.addWidget(card)

    def closeEvent(self, event):
        self.refresh_timer.stop()
        event.accept()

