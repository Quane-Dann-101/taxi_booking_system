from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QMenu, QGridLayout)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QIcon, QColor
from utils.session import current_session
from admin_dashboard.manage_bookings import ManageBookingsWindow
import os

class AdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setFixedSize(1200, 800)  # Increased size for better layout
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e272e;
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
                background-color: #2d3436;
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
                background-color: #00b894;
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
        
        # Enhanced Header
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #2d3436;
                color: white;
                border-bottom: 2px solid #00b894;
            }
        """)
        header_widget.setFixedHeight(80)
        header_layout = QHBoxLayout(header_widget)
        
        # Admin Title and Welcome Message
        title_container = QVBoxLayout()
        admin_title = QLabel("ADMIN DASHBOARD")
        admin_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #00b894;
            letter-spacing: 2px;
        """)
        welcome_label = QLabel(f"Welcome, {current_session.username}")
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            letter-spacing: 0.5px;
        """)
        title_container.addWidget(admin_title)
        title_container.addWidget(welcome_label)
        
        # Admin Profile Button
        user_button = QPushButton("⚙️  Admin")
        user_button.setObjectName("userButton")
        user_button.setFixedSize(120, 45)
        user_button.setStyleSheet("""
            QPushButton#userButton {
                font-size: 16px;
                border: 2px solid #00b894;
                border-radius: 22px;
                padding: 5px 15px;
                color: white;
                text-align: center;
                background-color: #2d3436;
            }
            QPushButton#userButton:hover {
                background-color: #00b894;
            }
        """)
        
        menu = QMenu(self)
        menu.addAction("Profile Settings")
        menu.addAction("System Preferences")
        menu.addSeparator()
        logout_action = menu.addAction("Logout")
        logout_action.triggered.connect(self.handle_logout)
        
        user_button.clicked.connect(lambda: menu.exec(user_button.mapToGlobal(
            QPoint(user_button.rect().right() - menu.sizeHint().width(), 
                  user_button.rect().bottom()))))

        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(user_button)
        
        layout.addWidget(header_widget)
        
        # Main Content Area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #1e272e;
                border-radius: 15px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        
        # Dashboard Options Grid
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(30)
        buttons_layout.setContentsMargins(40, 40, 40, 40)
        
        # Create admin action buttons with enhanced styling
        buttons_data = [
            ("Manage Users", "users_icon.png", "#e17055", self.show_manage_users),
            ("Manage Drivers", "drivers_icon.png", "#0984e3", self.show_manage_drivers),
            ("Manage Bookings", "bookings_icon.png", "#00b894", self.show_manage_bookings),
            ("System Analytics", "analytics_icon.png", "#6c5ce7", self.show_analytics),
            ("Reports", "reports_icon.png", "#fdcb6e", self.show_reports),
            ("Settings", "settings_icon.png", "#a8e6cf", self.show_settings)
        ]
        
        for index, (text, icon, color, handler) in enumerate(buttons_data):
            button = self.create_action_button(text, icon, color)
            button.clicked.connect(handler)
            buttons_layout.addWidget(button, index // 3, index % 3)
        
        content_layout.addLayout(buttons_layout)
        layout.addWidget(content_widget)
        
        # Status Bar
        status_bar = QLabel("System Status: Online | Last Updated: Just Now")
        status_bar.setStyleSheet("""
            color: #95a5a6;
            padding: 10px;
            font-size: 12px;
        """)
        layout.addWidget(status_bar)

    def create_action_button(self, text, icon_name, color):
        button = QPushButton()
        button.setFixedSize(300, 200)
        
        btn_layout = QVBoxLayout(button)
        btn_layout.setSpacing(15)
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", icon_name)
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            scaled_pixmap = icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: white;
            padding: 8px;
            letter-spacing: 0.5px;
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(text_label)
        btn_layout.addStretch()
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 15px;
                transition: all 0.3s;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            QPushButton:pressed {{
                transform: translateY(2px);
            }}
        """)
        
        return button

    def show_manage_users(self):
        pass

    def show_manage_drivers(self):
        pass

    def show_manage_bookings(self):
        self.manage_bookings_window = ManageBookingsWindow(self)
        self.manage_bookings_window.show()

    def show_analytics(self):
        pass

    def show_reports(self):
        pass

    def show_settings(self):
        pass
        
    def handle_logout(self):
        from login_window import LoginWindow
        current_session.clear_session()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
