from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QScrollArea, QFrame,
                           QGridLayout, QComboBox, QMessageBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QFont, QIcon
from utils.session import current_session
import sqlite3
import os
from datetime import datetime

class ShadowEffect(QGraphicsDropShadowEffect):
    def __init__(self):
        super().__init__()
        self.setBlurRadius(15)
        self.setXOffset(0)
        self.setYOffset(3)
        self.setColor(QColor(0, 0, 0, 60))

class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 26)
        
        colors = {
            'assigned': ('#4CAF50', '#E8F5E9'),
            'pending': ('#FFC107', '#FFF8E1'),
            'completed': ('#2196F3', '#E3F2FD'),
            'confirmed': ('#27ae60', '#E8F5E9'),
            'declined': ('#e74c3c', '#FFEBEE')
        }
        
        bg_color, light_bg = colors.get(status.lower(), ('#9E9E9E', '#F5F5F5'))
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {light_bg};
                color: {bg_color};
                border: 2px solid {bg_color};
                border-radius: 13px;
                padding: 0 8px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        
        self.setText(status.upper())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class RequestCard(QFrame):
    def __init__(self, request_data, parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self.setFixedHeight(250)  # Increased height to accommodate all content
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        self.setObjectName("requestCard")
        self.setStyleSheet("""
            QFrame#requestCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2C3E50, stop:1 #2C3E50);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QLabel {
                color: white;
            }
            QLabel#headerLabel {
                font-size: 15px;
                font-weight: bold;
                color: #ECF0F1;
            }
            QLabel#infoLabel {
                color: #BDC3C7;
                font-size: 13px;
            }
            QLabel#timeLabel {
                color: #3498DB;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#confirmBtn {
                background-color: #2ecc71;
                color: white;
                border: none;
            }
            QPushButton#confirmBtn:hover {
                background-color: #27ae60;
            }
            QPushButton#declineBtn {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton#declineBtn:hover {
                background-color: #c0392b;
            }
        """)
        
        shadow = ShadowEffect()
        self.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header Row
        header_layout = QHBoxLayout()
        booking_info = QHBoxLayout()
        booking_id = QLabel(f"Booking #{self.request_data['booking_id']}")
        booking_id.setObjectName("headerLabel")
        booking_info.addWidget(booking_id)
        
        status = StatusBadge(self.request_data['booking_status'])
        
        header_layout.addLayout(booking_info)
        header_layout.addStretch()
        header_layout.addWidget(status)
        
        # Customer Info Row
        customer_layout = QHBoxLayout()
        customer_name = QLabel(f"👤 {self.request_data['user_name']}")
        customer_name.setObjectName("headerLabel")
        admin_name = QLabel(f"📋 Assigned by: {self.request_data['admin_name'] or 'System'}")
        admin_name.setObjectName("infoLabel")
        customer_layout.addWidget(customer_name)
        customer_layout.addStretch()
        customer_layout.addWidget(admin_name)
        
        # Locations Container
        locations_frame = QFrame()
        locations_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        locations_layout = QVBoxLayout(locations_frame)
        locations_layout.setSpacing(8)
        locations_layout.setContentsMargins(12, 10, 12, 10)
        
        # Locations and Time
        pickup_layout = QHBoxLayout()
        pickup_location = QLabel(f"🔵 From: {self.request_data['pickup_location']}")
        pickup_location.setObjectName("infoLabel")
        pickup_location.setWordWrap(True)
        pickup_layout.addWidget(pickup_location)
        
        dropoff_layout = QHBoxLayout()
        dropoff_location = QLabel(f"📍 To: {self.request_data['dropoff_location']}")
        dropoff_location.setObjectName("infoLabel")
        dropoff_location.setWordWrap(True)
        dropoff_layout.addWidget(dropoff_location)
        
        time_layout = QHBoxLayout()
        pickup_time = QLabel(f"🕒 {self.request_data['pickup_time']}")
        pickup_time.setObjectName("timeLabel")
        time_layout.addWidget(pickup_time)
        time_layout.addStretch()
        
        locations_layout.addLayout(pickup_layout)
        locations_layout.addLayout(dropoff_layout)
        locations_layout.addLayout(time_layout)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        confirm_button = QPushButton("Confirm Trip")
        confirm_button.setObjectName("confirmBtn")
        confirm_button.clicked.connect(lambda: self.handle_confirm(self.request_data['booking_id']))
        
        decline_button = QPushButton("Decline")
        decline_button.setObjectName("declineBtn")
        decline_button.clicked.connect(lambda: self.handle_decline(self.request_data['booking_id']))
        
        action_layout.addStretch()
        action_layout.addWidget(confirm_button)
        action_layout.addWidget(decline_button)
        
        # Add all sections to main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(customer_layout)
        main_layout.addWidget(locations_frame)
        main_layout.addSpacing(5)
        main_layout.addLayout(action_layout)
        
    def setup_animations(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def handle_confirm(self, booking_id):
        reply = QMessageBox.question(
            self, 'Confirm Trip',
            'Are you sure you want to confirm this trip?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'database', 'taxi_booking.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE bookings 
                    SET booking_status = 'confirmed'
                    WHERE id = ? AND driver_id = ?
                ''', (booking_id, current_session.user_id))
                
                conn.commit()
                conn.close()
                
                # Find the main window and refresh
                main_window = self.window()
                if hasattr(main_window, 'refresh_requests'):
                    main_window.refresh_requests()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def handle_decline(self, booking_id):
        reply = QMessageBox.question(
            self, 'Decline Trip',
            'Are you sure you want to decline this trip?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
    
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'database', 'taxi_booking.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE bookings 
                    SET booking_status = 'declined'
                    WHERE id = ? AND driver_id = ?
                ''', (booking_id, current_session.user_id))
                
                conn.commit()
                conn.close()
                
                # Find the main window and refresh
                main_window = self.window()
                if hasattr(main_window, 'refresh_requests'):
                    main_window.refresh_requests()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
        

class ViewRequestsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Driver Dashboard - Trip Requests")
        self.setFixedSize(1200, 650)
        
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
            QScrollBar::handle:vertical:hover {
                background: #2980B9;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 12, 25, 12)
        
        # Header Section
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 12px;
                border: 1px solid rgba(52, 152, 219, 0.2);
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 8, 15, 8)
        
        # Title Section
        title_layout = QHBoxLayout()
        dashboard_icon = QLabel("🚖")
        dashboard_icon.setStyleSheet("font-size: 22px;")
        self.title_label = QLabel("Trip Requests")
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ECF0F1;
        """)
        title_layout.addWidget(dashboard_icon)
        title_layout.addWidget(self.title_label)
        
        # Sort Options
        sort_frame = QFrame()
        sort_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        sort_layout = QHBoxLayout(sort_frame)
        sort_layout.setContentsMargins(8, 4, 8, 4)
        
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet("color: #BDC3C7; font-size: 13px;")
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Latest First", "Earliest First", "Status"])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495E;
                color: white;
                padding: 6px;
                border: 1px solid #2C3E50;
                border-radius: 4px;
                min-width: 140px;
            }
            QComboBox:hover {
                border: 1px solid #3498DB;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.sort_combo.currentIndexChanged.connect(self.refresh_requests)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(sort_frame)
        
        # Requests Grid Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        layout.addWidget(header_widget)
        layout.addWidget(scroll_area)
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_requests)
        self.refresh_timer.start(30000)
        
        # Initial load
        self.refresh_requests()


    def refresh_requests(self):
        # Clear existing cards
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        try:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'database', 'taxi_booking.db')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sort_option = self.sort_combo.currentText()
            order_clause = {
                "Latest First": "ORDER BY b.pickup_time DESC",
                "Earliest First": "ORDER BY b.pickup_time ASC",
                "Status": "ORDER BY b.booking_status, b.pickup_time DESC"
            }.get(sort_option, "ORDER BY b.pickup_time DESC")
            
            cursor.execute(f'''
                SELECT 
                    b.id, 
                    u.username as user_name,
                    a.username as admin_name,
                    b.pickup_location, 
                    b.dropoff_location,
                    b.pickup_time, 
                    b.booking_status
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                LEFT JOIN admins a ON b.admin_id = a.id
                WHERE b.driver_id = ?
                {order_clause}
            ''', (current_session.user_id,))
            
            requests = cursor.fetchall()
            
            if not requests:
                self.show_empty_state()
            else:
                self.title_label.setText(f"Trip Requests ({len(requests)})")
                self.display_request_cards(requests)
            
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
        
        message_label = QLabel("No Assigned Trips")
        message_label.setStyleSheet("""
            color: #BDC3C7;
            font-size: 18px;
            font-weight: bold;
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_message = QLabel("New trips will appear here when assigned")
        sub_message.setStyleSheet("""
            color: #7F8C8D;
            font-size: 14px;
        """)
        sub_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(message_label)
        empty_layout.addWidget(sub_message)
        
        self.grid_layout.addWidget(empty_widget, 0, 0, 1, 2)

    def show_error_state(self, error_message):
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_label = QLabel("Unable to load requests")
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
        retry_button.clicked.connect(self.refresh_requests)
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(error_label)
        error_layout.addWidget(retry_button)
        
        self.grid_layout.addWidget(error_widget, 0, 0, 1, 2)

    def display_request_cards(self, requests):
        for i, request in enumerate(requests):
            request_data = {
                'booking_id': request[0],
                'user_name': request[1],
                'admin_name': request[2],
                'pickup_location': request[3],
                'dropoff_location': request[4],
                'pickup_time': request[5],
                'booking_status': request[6]
            }
            
            card = RequestCard(request_data)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)

    def closeEvent(self, event):
        self.refresh_timer.stop()
        event.accept()
