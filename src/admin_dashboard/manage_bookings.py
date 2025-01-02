from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                           QHBoxLayout, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from utils.session import current_session
import sqlite3
import os

class ManageBookingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Bookings")
        self.setFixedSize(1200, 800)
        
        # Get database path once during initialization
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   'database', 'taxi_booking.db')
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e272e;
            }
            QTableWidget {
                background-color: #2d3436;
                color: white;
                gridline-color: #1e272e;
                border-radius: 5px;
                padding: 10px;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d566e;
            }
            QTableWidget::item:selected {
                background-color: #00b894;
            }
            QHeaderView::section {
                background-color: #2d3436;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
            QComboBox {
                background-color: #2d3436;
                color: white;
                padding: 6px;
                border: 1px solid #3d566e;
                border-radius: 5px;
                min-width: 200px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid #00b894;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3436;
                color: white;
                selection-background-color: #00b894;
                selection-color: white;
                border: 1px solid #3d566e;
                padding: 5px;
                min-width: 200px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with centered title
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00b894;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #00d8b4;
            }
        """)
        back_btn.clicked.connect(self.close)
        
        # Centered title
        header = QLabel("Booking Management")
        header.setStyleSheet("""
            font-size: 24px;
            color: white;
            font-weight: bold;
            padding-bottom: 10px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Filter options
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Sort by Date (Newest First)", 
            "Sort by Date (Oldest First)",
            "Sort by ID (Highest First)", 
            "Sort by ID (Lowest First)"
        ])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: 1px solid #3d566e;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        self.sort_combo.currentIndexChanged.connect(self.apply_filter)
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addStretch()
        
        # Add all header elements with proper spacing
        header_layout.addWidget(back_btn, 1)
        header_layout.addWidget(header, 4)
        header_layout.addWidget(filter_container, 1)
        
        # Table setup
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(8)
        self.bookings_table.setHorizontalHeaderLabels([
            "Booking ID", "User", "Pickup Location", "Dropoff Location", 
            "Pickup Time", "Status", "Fare", "Driver Assignment"
        ])
        
        # Column widths
        self.bookings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.bookings_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.bookings_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.bookings_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.bookings_table.setColumnWidth(0, 85)
        self.bookings_table.setColumnWidth(5, 80)
        self.bookings_table.setColumnWidth(6, 80)
        self.bookings_table.setColumnWidth(7, 200)

        for i in [1, 2, 3, 4]:
            self.bookings_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        self.bookings_table.setAlternatingRowColors(True)
        self.bookings_table.setWordWrap(True)
        self.bookings_table.verticalHeader().setDefaultSectionSize(50)
        
        # Layout
        layout.addWidget(header_container)
        layout.addWidget(self.bookings_table)
        
        # Load initial data
        self.load_bookings()

    def get_status_color(self, status):
        status_colors = {
            'pending': '#f1c40f',    # Yellow
            'assigned': '#3498db',    # Blue
            'refused': '#e74c3c',     # Red
            'accepted': '#2ecc71',    # Green
            'on_the_way': '#9b59b6',  # Purple
            'completed': '#27ae60',   # Dark Green
            'cancelled': '#c0392b'    # Dark Red
        }
        return status_colors.get(status, '#95a5a6')

    def create_driver_widget(self, booking_id, current_status, current_driver=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 0, 5, 0)

        driver_combo = QComboBox()
        driver_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d3436;
                color: white;
                padding: 6px;
                border: 1px solid #3d566e;
                border-radius: 5px;
                min-width: 180px;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3436;
                color: white;
                selection-background-color: #00b894;
                selection-color: white;
                border: 1px solid #3d566e;
                padding: 5px;
            }
        """)

        if current_status == 'pending':
            self.load_available_drivers(driver_combo)
            driver_combo.currentIndexChanged.connect(
                lambda index, b_id=booking_id, combo=driver_combo: 
                self.handle_driver_selection(b_id, combo) if index > 0 else None
            )
        else:
            driver_combo.addItem(current_driver if current_driver else "Not Assigned")
            driver_combo.addItem("⚠ Unassign Driver")
            driver_combo.currentIndexChanged.connect(
                lambda index, b_id=booking_id: 
                self.unassign_driver(b_id) if index == 1 else None
            )

        layout.addWidget(driver_combo)
        return container

    def apply_filter(self):
        sort_option = self.sort_combo.currentText()
        if "Date" in sort_option:
            order = "DESC" if "Newest" in sort_option else "ASC"
            self.load_bookings(f"ORDER BY b.pickup_time {order}")
        else:
            order = "DESC" if "Highest" in sort_option else "ASC"
            self.load_bookings(f"ORDER BY b.id {order}")

    def load_bookings(self, order_clause="ORDER BY b.created_at DESC"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = f'''
                SELECT b.id, u.username, b.pickup_location, b.dropoff_location,
                       b.pickup_time, b.booking_status, b.fare, d.username
                FROM bookings b
                LEFT JOIN users u ON b.user_id = u.id
                LEFT JOIN drivers d ON b.driver_id = d.id
                {order_clause}
            '''
            
            cursor.execute(query)
            bookings = cursor.fetchall()
            self.bookings_table.setRowCount(len(bookings))

            for row, booking in enumerate(bookings):
                for col, value in enumerate(booking):
                    if col != 7:  # Skip driver assignment column
                        item = QTableWidgetItem(str(value if value is not None else '-'))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if col == 5:  # Status column
                            item.setForeground(QColor(self.get_status_color(value)))
                        self.bookings_table.setItem(row, col, item)
                
                driver_widget = self.create_driver_widget(booking[0], booking[5], booking[7])
                self.bookings_table.setCellWidget(row, 7, driver_widget)

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to load bookings: {str(e)}")
        finally:
            conn.close()

    def load_available_drivers(self, combo_box):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT d.username 
                FROM drivers d
                WHERE d.id NOT IN (
                    SELECT driver_id 
                    FROM bookings 
                    WHERE booking_status = 'assigned'
                    AND driver_id IS NOT NULL
                )
            ''')
            drivers = cursor.fetchall()
            
            combo_box.clear()
            combo_box.addItem("Select Driver")
            for driver in drivers:
                combo_box.addItem(driver[0])
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to load drivers: {str(e)}")
        finally:
            conn.close()

    def handle_driver_selection(self, booking_id, driver_combo):
        selected_driver = driver_combo.currentText()
        reply = QMessageBox.question(self, 'Confirm Assignment',
                                   f'Do you want to assign driver "{selected_driver}" to this booking?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.assign_driver(booking_id, selected_driver)
        else:
            driver_combo.setCurrentIndex(0)

    def assign_driver(self, booking_id, selected_driver):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM drivers WHERE username = ?', (selected_driver,))
            driver_id = cursor.fetchone()[0]
            
            cursor.execute('''
                UPDATE bookings 
                SET driver_id = ?, booking_status = "assigned", admin_id = ?
                WHERE id = ?
            ''', (driver_id, current_session.user_id, booking_id))
            
            conn.commit()
            QMessageBox.information(self, "Success", f"Driver {selected_driver} has been assigned successfully!")
            self.load_bookings()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to assign driver: {str(e)}")
        finally:
            conn.close()

    def unassign_driver(self, booking_id):
        reply = QMessageBox.question(self, 'Confirm Unassign',
                                   'Are you sure you want to unassign the driver from this booking?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE bookings 
                    SET driver_id = NULL, booking_status = "pending", admin_id = NULL
                    WHERE id = ?
                ''', (booking_id,))
                
                conn.commit()
                QMessageBox.information(self, "Success", "Driver has been unassigned successfully!")
                self.load_bookings()
                
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to unassign driver: {str(e)}")
            finally:
                conn.close()
