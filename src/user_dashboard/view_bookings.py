from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                           QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from utils.session import current_session
import sqlite3
import os

class ViewBookingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Bookings")
        self.setFixedSize(1000, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QTableWidget {
                background-color: #34495e;
                color: white;
                gridline-color: #2c3e50;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3d566e;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top bar with back button and title
        top_bar = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        back_btn.clicked.connect(self.close)
        
        header = QLabel("My Bookings")
        header.setStyleSheet("""
            font-size: 28px;
            color: white;
            font-weight: bold;
            margin: 20px;
        """)
        
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        top_bar.addWidget(header)
        top_bar.addStretch()

        # Create and setup table
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(6)
        self.bookings_table.setHorizontalHeaderLabels([
            "Pickup Location", "Dropoff Location", 
            "Pickup Time", "Status", "Fare", "Assigned Driver"
        ])
        
        # Enable text wrapping and set row height
        self.bookings_table.setWordWrap(True)
        self.bookings_table.verticalHeader().setDefaultSectionSize(60)
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bookings_table.setAlternatingRowColors(True)
        self.bookings_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #2c3e50;
            }
            QTableWidget::item {
                border-radius: 4px;
                margin: 2px;
            }
        """)

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_btn.clicked.connect(self.load_bookings)

        # Layout setup
        layout.addLayout(top_bar)
        layout.addWidget(self.bookings_table)
        
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(refresh_btn)
        layout.addLayout(button_container)
        
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.load_bookings()

    def get_day_suffix(self, day):
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return suffix

    def load_bookings(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'database', 'taxi_booking.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT b.pickup_location, b.dropoff_location, b.pickup_time, 
                       b.booking_status, b.fare, d.username as driver_name
                FROM bookings b
                LEFT JOIN drivers d ON b.driver_id = d.id
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
            ''', (current_session.user_id,))
            
            bookings = cursor.fetchall()
            self.bookings_table.setRowCount(len(bookings))

            for row, booking in enumerate(bookings):
                # Convert date string to desired format
                date_str = booking[2]  # Format: "01/01/2025 12:00 AM"
                date_obj = QDateTime.fromString(date_str, "dd/MM/yyyy hh:mm AP")
                formatted_date = (date_obj.toString("MMMM d") + 
                                self.get_day_suffix(date_obj.date().day()) + 
                                date_obj.toString(" yyyy") +
                                date_obj.toString(" hh:mm AP"))


                self.bookings_table.verticalHeader().setDefaultSectionSize(80)  # Increased row height
                self.bookings_table.setWordWrap(True)
                self.bookings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # For date 

                # Status with color coding
                status_item = QTableWidgetItem(booking[3])
                if booking[3] == 'pending':
                    status_item.setForeground(QColor('#f1c40f'))
                elif booking[3] == 'completed':
                    status_item.setForeground(QColor('#2ecc71'))
                elif booking[3] == 'cancelled':
                    status_item.setForeground(QColor('#e74c3c'))

                # Create table items
                pickup_item = QTableWidgetItem(booking[0])
                dropoff_item = QTableWidgetItem(booking[1])
                date_item = QTableWidgetItem(formatted_date)
                fare_item = QTableWidgetItem(f"TTD ${booking[4]}")
                driver_item = QTableWidgetItem(booking[5] if booking[5] else "Pending Assignment")

                # Set alignment for all items
                for item in [pickup_item, dropoff_item, date_item, status_item, fare_item, driver_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

                # Add items to table
                self.bookings_table.setItem(row, 0, pickup_item)
                self.bookings_table.setItem(row, 1, dropoff_item)
                self.bookings_table.setItem(row, 2, date_item)
                self.bookings_table.setItem(row, 3, status_item)
                self.bookings_table.setItem(row, 4, fare_item)
                self.bookings_table.setItem(row, 5, driver_item)

            # Adjust columns to content
            self.bookings_table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to load bookings: {str(e)}")
        finally:
            conn.close()
