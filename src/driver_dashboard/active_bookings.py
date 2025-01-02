from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QScrollArea, QFrame,
                           QGridLayout, QComboBox, QMessageBox, QGraphicsDropShadowEffect,
                           QDialog, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from utils.session import current_session
import sqlite3
import os

class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 26)
        
        colors = {
            'confirmed': ('#27ae60', '#E8F5E9'),
            'on_the_way': ('#2980b9', '#E3F2FD'),
            'completed': ('#2ecc71', '#E8F5E9'),
            'incomplete': ('#e74c3c', '#FFEBEE')
        }
        
        bg_color, light_bg = colors.get(status.lower(), ('#95a5a6', '#F5F5F5'))
        
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
        
        self.setText(status.upper().replace('_', ' '))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class CancellationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Trip Cancellation")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Explanation label
        label = QLabel("Please provide a reason for cancellation:")
        label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold;")
        
        # Reason text input
        self.reason_input = QTextEdit()
        self.reason_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                background: white;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Buttons
        button_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit")
        cancel_btn = QPushButton("Cancel")
        
        for btn in [submit_btn, cancel_btn]:
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        
        cancel_btn.setStyleSheet(cancel_btn.styleSheet().replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b"))
        
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(label)
        layout.addWidget(self.reason_input)
        layout.addLayout(button_layout)
        
        submit_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)


class ActiveBookingCard(QFrame):
    def __init__(self, booking_data, parent=None):
        super().__init__(parent)
        self.booking_data = booking_data
        self.setFixedHeight(250)
        self.setup_ui()
        
    def setup_ui(self):
        self.setObjectName("activeBookingCard")
        self.setStyleSheet("""
            QFrame#activeBookingCard {
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
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#startBtn {
                background-color: #2ecc71;
                color: white;
                border: none;
            }
            QPushButton#startBtn:hover {
                background-color: #27ae60;
            }
            QPushButton#completeBtn {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton#completeBtn:hover {
                background-color: #2980b9;
            }
            QPushButton#cancelBtn {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background-color: #c0392b;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with Booking ID and Status
        header_layout = QHBoxLayout()
        booking_id = QLabel(f"Booking #{self.booking_data['booking_id']}")
        booking_id.setObjectName("headerLabel")
        status = StatusBadge(self.booking_data['status'])
        header_layout.addWidget(booking_id)
        header_layout.addStretch()
        header_layout.addWidget(status)
        
        # Customer Info
        customer_info = QLabel(f"👤 {self.booking_data['customer_name']}")
        customer_info.setObjectName("headerLabel")
        
        # Trip Details Container
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        
        pickup = QLabel(f"🔵 From: {self.booking_data['pickup_location']}")
        dropoff = QLabel(f"📍 To: {self.booking_data['dropoff_location']}")
        time = QLabel(f"🕒 {self.booking_data['pickup_time']}")
        
        for label in [pickup, dropoff, time]:
            label.setObjectName("infoLabel")
            label.setWordWrap(True)
            details_layout.addWidget(label)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        if self.booking_data['status'] == 'confirmed':
            start_btn = QPushButton("Start Trip")
            start_btn.setObjectName("startBtn")
            start_btn.clicked.connect(self.start_trip)
            action_layout.addWidget(start_btn)
            
        elif self.booking_data['status'] == 'on_the_way':
            complete_btn = QPushButton("Complete Trip")
            complete_btn.setObjectName("completeBtn")
            complete_btn.clicked.connect(self.complete_trip)
            action_layout.addWidget(complete_btn)
            
            cancel_btn = QPushButton("Cancel Trip")
            cancel_btn.setObjectName("cancelBtn")
            cancel_btn.clicked.connect(self.cancel_trip)
            action_layout.addWidget(cancel_btn)
        
        # Add all sections to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(customer_info)
        main_layout.addWidget(details_frame)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)


    def start_trip(self):
        reply = QMessageBox.question(
            self, 'Start Trip',
            'Are you ready to start this trip?',
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
                    SET booking_status = 'on_the_way'
                    WHERE id = ? AND driver_id = ?
                ''', (self.booking_data['booking_id'], current_session.user_id))
                
                conn.commit()
                conn.close()
                
                # Refresh the parent window
                main_window = self.window()
                if hasattr(main_window, 'refresh_bookings'):
                    main_window.refresh_bookings()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def complete_trip(self):
        reply = QMessageBox.question(
            self, 'Complete Trip',
            'Has the trip been completed successfully?',
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
                    SET booking_status = 'completed'
                    WHERE id = ? AND driver_id = ?
                ''', (self.booking_data['booking_id'], current_session.user_id))
                
                conn.commit()
                conn.close()
                
                main_window = self.window()
                if hasattr(main_window, 'refresh_bookings'):
                    main_window.refresh_bookings()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def cancel_trip(self):
        dialog = CancellationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.reason_input.toPlainText().strip():
            try:
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'database', 'taxi_booking.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE bookings 
                    SET booking_status = 'incomplete',
                        cancellation_reason = ?
                    WHERE id = ? AND driver_id = ?
                ''', (dialog.reason_input.toPlainText(), 
                     self.booking_data['booking_id'], 
                     current_session.user_id))
                
                conn.commit()
                conn.close()
                
                main_window = self.window()
                if hasattr(main_window, 'refresh_bookings'):
                    main_window.refresh_bookings()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")


class ActiveBookingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Active Bookings")
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
        dashboard_icon = QLabel("🚗")
        dashboard_icon.setStyleSheet("font-size: 22px;")
        self.title_label = QLabel("Active Bookings")
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ECF0F1;
        """)
        title_layout.addWidget(dashboard_icon)
        title_layout.addWidget(self.title_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Bookings Grid Area
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
        self.refresh_timer.timeout.connect(self.refresh_bookings)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial load
        self.refresh_bookings()

    def refresh_bookings(self):
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
            
            cursor.execute('''
                SELECT 
                    b.id, 
                    u.username as customer_name,
                    b.pickup_location, 
                    b.dropoff_location,
                    b.pickup_time, 
                    b.booking_status
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                WHERE b.driver_id = ? 
                AND b.booking_status IN ('confirmed', 'on_the_way')
                ORDER BY 
                    CASE b.booking_status
                        WHEN 'on_the_way' THEN 1
                        WHEN 'confirmed' THEN 2
                    END,
                    b.pickup_time ASC
            ''', (current_session.user_id,))
            
            active_bookings = cursor.fetchall()
            
            if not active_bookings:
                self.show_empty_state()
            else:
                self.title_label.setText(f"Active Bookings ({len(active_bookings)})")
                self.display_booking_cards(active_bookings)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.show_error_state(str(e))

    def show_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("🚗")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QLabel("No Active Bookings")
        message_label.setStyleSheet("""
            color: #BDC3C7;
            font-size: 18px;
            font-weight: bold;
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_message = QLabel("Your ongoing trips will appear here")
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
        
        error_label = QLabel("Unable to load bookings")
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
        retry_button.clicked.connect(self.refresh_bookings)
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(error_label)
        error_layout.addWidget(retry_button)
        
        self.grid_layout.addWidget(error_widget, 0, 0, 1, 2)

    def display_booking_cards(self, bookings):
        for i, booking in enumerate(bookings):
            booking_data = {
                'booking_id': booking[0],
                'customer_name': booking[1],
                'pickup_location': booking[2],
                'dropoff_location': booking[3],
                'pickup_time': booking[4],
                'status': booking[5]
            }
            
            card = ActiveBookingCard(booking_data)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)

    def closeEvent(self, event):
        self.refresh_timer.stop()
        event.accept()
