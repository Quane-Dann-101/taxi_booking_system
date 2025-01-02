from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QScrollArea, QFrame,
                           QGridLayout, QComboBox, QMessageBox, QGraphicsDropShadowEffect,
                           QDialog, QCalendarWidget)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QColor
from utils.session import current_session
import sqlite3
import os
from datetime import datetime

class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 26)
        
        colors = {
            'completed': ('#2ecc71', '#E8F5E9'),
            'incomplete': ('#e74c3c', '#FFEBEE'),
            'cancelled': ('#95a5a6', '#F5F5F5')
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
        
        self.setText(status.upper())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class HistoryCard(QFrame):
    def __init__(self, trip_data, parent=None):
        super().__init__(parent)
        self.trip_data = trip_data
        self.setFixedHeight(220)
        self.setup_ui()
    def setup_ui(self):
        self.setObjectName("historyCard")
        self.setStyleSheet("""
            QFrame#historyCard {
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
                background-color: rgba(52, 152, 219, 0.1);
                color: #3498DB;
                border: 1px solid #3498DB;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.2);
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with Booking ID, Date and Status
        header_layout = QHBoxLayout()
        booking_info = QHBoxLayout()
        
        booking_id = QLabel(f"Booking #{self.trip_data['booking_id']}")
        booking_id.setObjectName("headerLabel")
        
        date_label = QLabel(self.trip_data['completion_date'])
        date_label.setObjectName("timeLabel")
        
        status = StatusBadge(self.trip_data['status'])
        
        booking_info.addWidget(booking_id)
        booking_info.addWidget(date_label)
        
        header_layout.addLayout(booking_info)
        header_layout.addStretch()
        header_layout.addWidget(status)
        
        # Customer Info
        customer_layout = QHBoxLayout()
        customer_name = QLabel(f"👤 {self.trip_data['customer_name']}")
        customer_name.setObjectName("headerLabel")
        customer_layout.addWidget(customer_name)
        
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
        details_layout.setSpacing(8)
        
        # Location Details
        pickup = QLabel(f"🔵 From: {self.trip_data['pickup_location']}")
        dropoff = QLabel(f"📍 To: {self.trip_data['dropoff_location']}")
        time = QLabel(f"🕒 Trip Time: {self.trip_data['pickup_time']}")
        
        for label in [pickup, dropoff, time]:
            label.setObjectName("infoLabel")
            label.setWordWrap(True)
            details_layout.addWidget(label)
        
        # If trip was incomplete, show reason
        if self.trip_data['status'].lower() == 'incomplete' and self.trip_data.get('cancellation_reason'):
            reason_label = QLabel(f"❌ Cancellation Reason: {self.trip_data['cancellation_reason']}")
            reason_label.setObjectName("infoLabel")
            reason_label.setWordWrap(True)
            reason_label.setStyleSheet("color: #e74c3c;")
            details_layout.addWidget(reason_label)
        
        # Add all sections to main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(customer_layout)
        main_layout.addWidget(details_frame)

class BookingHistoryWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Booking History")
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
            QComboBox {
                background-color: #34495E;
                color: white;
                padding: 6px;
                border: 1px solid #2C3E50;
                border-radius: 4px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #3498DB;
            }
            QComboBox::drop-down {
                border: none;
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
        history_icon = QLabel("📋")
        history_icon.setStyleSheet("font-size: 22px;")
        self.title_label = QLabel("Trip History")
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ECF0F1;
        """)
        title_layout.addWidget(history_icon)
        title_layout.addWidget(self.title_label)
        
        # Filter Options
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(8, 4, 8, 4)
        
        # Status Filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #BDC3C7; font-size: 13px;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Completed", "Incomplete"])
        
        # Date Filter
        date_label = QLabel("Period:")
        date_label.setStyleSheet("color: #BDC3C7; font-size: 13px;")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["All Time", "Today", "This Week", "This Month"])
        
        for widget in [status_label, self.status_combo, date_label, self.period_combo]:
            filter_layout.addWidget(widget)
        
        # Connect filters to refresh
        self.status_combo.currentIndexChanged.connect(self.refresh_history)
        self.period_combo.currentIndexChanged.connect(self.refresh_history)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(filter_frame)
        
        # History Grid Area
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
        
        # Initial load
        self.refresh_history()

    def refresh_history(self):
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
            
            # Build query based on filters
            status_filter = self.status_combo.currentText()
            period_filter = self.period_combo.currentText()
            
            query = '''
                SELECT 
                    b.id, 
                    u.username as customer_name,
                    b.pickup_location, 
                    b.dropoff_location,
                    b.pickup_time, 
                    b.booking_status,
                    b.pickup_time as completion_time
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                WHERE b.driver_id = ? 
                AND b.booking_status IN ('completed', 'incomplete')
            '''
            
            params = [current_session.user_id]
            
            # Add status filter
            if status_filter != "All":
                query += " AND b.booking_status = ?"
                params.append(status_filter.lower())
            
            # Add date filter
            if period_filter != "All Time":
                today = datetime.now().date()
                if period_filter == "Today":
                    query += " AND DATE(b.pickup_time) = DATE('now')"
                elif period_filter == "This Week":
                    query += " AND b.pickup_time >= DATE('now', '-7 days')"
                elif period_filter == "This Month":
                    query += " AND b.pickup_time >= DATE('now', '-30 days')"
            
            query += " ORDER BY b.pickup_time DESC"
            
            cursor.execute(query, params)
            history_records = cursor.fetchall()
            
            if not history_records:
                self.show_empty_state()
            else:
                self.title_label.setText(f"Trip History ({len(history_records)})")
                self.display_history_cards(history_records)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.show_error_state(str(e))


    def show_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("📋")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QLabel("No Trip History Found")
        message_label.setStyleSheet("""
            color: #BDC3C7;
            font-size: 18px;
            font-weight: bold;
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_message = QLabel("Completed trips will appear here")
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
        
        error_label = QLabel("Unable to load trip history")
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
        retry_button.clicked.connect(self.refresh_history)
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(error_label)
        error_layout.addWidget(retry_button)
        
        self.grid_layout.addWidget(error_widget, 0, 0, 1, 2)

    def display_history_cards(self, records):
        print("Displaying records:", records)  # Debug print
        for i, record in enumerate(records):
            trip_data = {
                'booking_id': record[0],
                'customer_name': record[1],
                'pickup_location': record[2],
                'dropoff_location': record[3],
                'pickup_time': record[4],
                'status': record[5],
                'completion_date': record[6]
            }
            print(f"Creating card for trip: {trip_data}")  # Debug print
            
            card = HistoryCard(trip_data)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)

