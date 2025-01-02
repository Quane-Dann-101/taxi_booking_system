from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QMenu, QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter
import os
from utils.session import current_session

class DriverDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driver Dashboard")
        self.setFixedSize(1200, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2d;
            }
            QWidget {
                color: #ffffff;
            }
            QPushButton#userButton {
                border: none;
                border-radius: 20px;
                padding: 5px;
                color: #ecf0f1;
                background-color: rgba(52, 58, 64, 0.7);
            }
            QPushButton#userButton:hover {
                background-color: #2c2c3c;
            }
            QMenu {
                background-color: #2c2c3c;
                border: 1px solid #343a40;
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
                background-color: #00b894;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #343a40;
                margin: 6px 15px;
            }
            QFrame#statusFrame {
                background-color: #2c2c3c;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #343a40;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with enhanced shadow effect
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #2c2c3c;
                color: white;
                border-bottom: 2px solid #343a40;
            }
        """)
        header_widget.setFixedHeight(80)
        header_layout = QHBoxLayout(header_widget)
        
        # Welcome message with driver name
        welcome_label = QLabel(f"Welcome back, {current_session.username}")
        welcome_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding-left: 25px;
            letter-spacing: 0.5px;
        """)
        
        # Enhanced status indicator
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-size: 15px;")
        
        self.status_button = QPushButton("Available")
        self.status_button.setCheckable(True)
        self.status_button.setChecked(True)
        self.status_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 13px;
                background-color: #00b894;
                border: 1px solid #00a884;
            }
            QPushButton:checked {
                background-color: #ff6b6b;
                border: 1px solid #ff5f5f;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        self.status_button.clicked.connect(self.toggle_status)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_button)
        
        # Enhanced user menu button
        user_button = QPushButton("⏣  ﹀")
        user_button.setObjectName("userButton")
        user_button.setFixedSize(100, 40)
        user_button.setStyleSheet("""
            QPushButton#userButton {
                font-size: 16px;
                border: none;
                border-radius: 20px;
                padding: 5px;
                color: white;
                text-align: center;
                background-color: #343a40;
            }
            QPushButton#userButton:hover {
                background-color: #2c2c3c;
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
        header_layout.addWidget(status_frame)
        header_layout.addWidget(user_button)
        
        # Enhanced main content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e2d;
                border-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        
        # Action buttons with improved layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        buttons_layout.setContentsMargins(40, 40, 40, 40)
        
        view_requests_btn = self.create_action_button(
            "View Requests", "requests_icon.png",
            "View and manage new booking requests"
        )
        view_requests_btn.clicked.connect(self.show_requests)
        
        active_bookings_btn = self.create_action_button(
            "Active Bookings", "active_icon.png",
            "Track and manage your ongoing trips"
        )
        active_bookings_btn.clicked.connect(self.show_active_bookings)
        
        booking_history_btn = self.create_action_button(
            "Booking History", "history_icon.png",
            "View your completed trips and earnings"
        )
        booking_history_btn.clicked.connect(self.show_booking_history)
        
        buttons_layout.addWidget(view_requests_btn)
        buttons_layout.addWidget(active_bookings_btn)
        buttons_layout.addWidget(booking_history_btn)
        
        content_layout.addLayout(buttons_layout)
        
        layout.addWidget(header_widget)
        layout.addWidget(content_widget)
        
    def create_action_button(self, text, icon_name, description=""):
        button = QPushButton()
        button.setFixedSize(320, 320)
        
        btn_layout = QVBoxLayout(button)
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(20, 25, 20, 25)
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", icon_name)
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            scaled_pixmap = icon_pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            padding: 8px;
        """)
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #a8a8b3;
            padding: 0px 15px;
        """)
        
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(text_label)
        btn_layout.addWidget(desc_label)
        
        button.setStyleSheet("""
            QPushButton {
                background-color: #2c2c3c;
                border: 1px solid #343a40;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #343a40;
                border: 1px solid #00b894;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #2c2c3c;
                transform: translateY(1px);
            }
        """)
        
        return button
    
    def toggle_status(self):
        if self.status_button.isChecked():
            self.status_button.setText("Unavailable")
        else:
            self.status_button.setText("Available")
    
    def show_requests(self):
        from driver_dashboard.view_requests import ViewRequestsWindow
        self.requests_window = ViewRequestsWindow(self)
        self.requests_window.show()
    
    def show_active_bookings(self):
        from driver_dashboard.active_bookings import ActiveBookingsWindow
        self.active_bookings_window = ActiveBookingsWindow(self)
        self.active_bookings_window.show()
    
    def show_booking_history(self):
        from driver_dashboard.booking_history import BookingHistoryWindow
        self.booking_history_window = BookingHistoryWindow(self)
        self.booking_history_window.show()
        pass
        
    def handle_logout(self):
        from login_window import LoginWindow
        current_session.clear_session()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
