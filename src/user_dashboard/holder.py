from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QLineEdit, QTimeEdit, 
                           QCalendarWidget, QDialog, QFrame, QMessageBox, QCompleter,
                           QGraphicsView, QGraphicsScene)
from PyQt6.QtCore import Qt, QDateTime, QUrl, QStringListModel
from PyQt6.QtGui import QPixmap, QPen, QColor, QPainter
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWebEngineWidgets import QWebEngineView
from utils.session import current_session
import sqlite3
import os
import json
from math import radians, sin, cos, sqrt, atan2


class LocationSearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search location in Trinidad...")
        
        # Initialize location_data attribute
        self.location_data = None
        
        # Enhanced network manager setup
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_response)
        
        # Create a more interactive completer
        self.completer = QCompleter()
        self.completer.setMaxVisibleItems(5)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer)
        
        # Add delayed search trigger
        self.textChanged.connect(self.search_location)
        
    def search_location(self, text):
        if len(text) > 2:  # Start searching after 2 characters
            url = QUrl("https://nominatim.openstreetmap.org/search")
            url.setQuery(f"q={text}, Trinidad and Tobago&format=json&limit=5")
            request = QNetworkRequest(url)
            request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "TaxiBookingApp/1.0")
            self.network_manager.get(request)
    
    def handle_response(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = json.loads(str(reply.readAll(), 'utf-8'))
            self.location_data = data
            suggestions = [result['display_name'] for result in data]
            
            # Update completer with new suggestions
            self.completer.setModel(QStringListModel(suggestions))
            self.completer.complete()
        reply.deleteLater()


class DateTimePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date and Time")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog { background-color: #2c3e50; }
            QLabel { color: white; font-size: 14px; margin-top: 10px; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget { background-color: #34495e; color: white; }
            QCalendarWidget QToolButton { 
                color: white; 
                background-color: #2c3e50; 
                padding: 5px; 
                border-radius: 3px; 
            }
            QCalendarWidget QMenu { 
                background-color: #34495e; 
                color: white; 
                padding: 5px; 
            }
            QCalendarWidget QSpinBox { 
                background-color: #34495e; 
                color: white; 
                padding: 3px; 
                border: 1px solid #2c3e50; 
            }
            QCalendarWidget QTableView { 
                background-color: #34495e; 
                selection-background-color: #4CAF50;
                selection-color: white;
                alternate-background-color: #3d566e;
            }
        """)
        
        time_label = QLabel("Select Time:")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 5px;
                min-height: 30px;
            }
        """)
        
        confirm_button = QPushButton("Confirm")
        confirm_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                margin-top: 15px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        confirm_button.clicked.connect(self.accept)
        
        layout.addWidget(self.calendar)
        layout.addWidget(time_label)
        layout.addWidget(self.time_edit)
        layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)


class MapView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #34495e; border-radius: 10px;")
        
        # Create web view for map
        self.web_view = QWebEngineView(self)
        self.setViewport(self.web_view)
        
        # HTML for OpenStreetMap with Leaflet
        html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
                <style>
                    body { margin: 0; }
                    #map { height: 100vh; }
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([10.6918, -61.2225], 9);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(map);
                    
                    var markers = [];
                    var route;
                    
                    function updateMarkers(pickup, dropoff) {
                        // Clear existing markers
                        markers.forEach(m => map.removeLayer(m));
                        markers = [];
                        
                        if (pickup) {
                            markers.push(L.marker([pickup.lat, pickup.lng])
                                .bindPopup('Pickup Location')
                                .addTo(map));
                        }
                        if (dropoff) {
                            markers.push(L.marker([dropoff.lat, dropoff.lng])
                                .bindPopup('Dropoff Location')
                                .addTo(map));
                        }
                        
                        if (pickup && dropoff) {
                            if (route) map.removeLayer(route);
                            route = L.polyline([
                                [pickup.lat, pickup.lng],
                                [dropoff.lat, dropoff.lng]
                            ], {color: 'blue'}).addTo(map);
                            map.fitBounds(route.getBounds());
                        }
                    }
                </script>
            </body>
            </html>
        '''
        self.web_view.setHtml(html)
        
    def update_points(self, pickup_coords=None, dropoff_coords=None):
        if pickup_coords and dropoff_coords:
            js_code = f'''
                updateMarkers(
                    {{lat: {pickup_coords[0]}, lng: {pickup_coords[1]}}},
                    {{lat: {dropoff_coords[0]}, lng: {dropoff_coords[1]}}}
                );
            '''
            self.web_view.page().runJavaScript(js_code)


class CreateBookingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Booking")
        self.setFixedSize(1200, 800)
        
        self.current_fare = 0.0
        self.pickup_coords = None
        self.dropoff_coords = None
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left Column
        left_column = self.setup_left_column()
        
        # Map
        self.map_view = MapView()
        
        main_layout.addWidget(left_column)
        main_layout.addWidget(self.map_view)
        
    def setup_left_column(self):
        left_column = QWidget()
        left_column.setFixedWidth(400)
        left_column.setStyleSheet("background-color: #2c3e50; color: white;")
        left_layout = QVBoxLayout(left_column)
        
        title_label = QLabel("Create New Booking")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.pickup_input = LocationSearchBar()
        self.dropoff_input = LocationSearchBar()
        self.datetime_input = QLineEdit()
        self.datetime_input.setReadOnly(True)
        self.datetime_input.setPlaceholderText("Click to select date and time")
        self.datetime_input.mousePressEvent = lambda _: self.show_datetime_picker()
        
        self.pickup_input.textChanged.connect(self.update_map)
        self.dropoff_input.textChanged.connect(self.update_map)
        
        input_style = """
            QLineEdit {
                padding: 12px;
                background-color: #34495e;
                border: none;
                border-radius: 5px;
                color: white;
            }
        """
        for widget in [self.pickup_input, self.dropoff_input, self.datetime_input]:
            widget.setStyleSheet(input_style)
        
        self.fare_container = self.setup_fare_container()
        
        create_button = QPushButton("Create Booking")
        create_button.setStyleSheet("""
            QPushButton {
                padding: 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        create_button.clicked.connect(self.handle_submit)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(QLabel("Pickup Location"))
        left_layout.addWidget(self.pickup_input)
        left_layout.addWidget(QLabel("Dropoff Location"))
        left_layout.addWidget(self.dropoff_input)
        left_layout.addWidget(QLabel("Pickup Date & Time"))
        left_layout.addWidget(self.datetime_input)
        left_layout.addWidget(self.fare_container)
        left_layout.addWidget(create_button)
        left_layout.addStretch()
        
        return left_column
        
    def setup_fare_container(self):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QLabel { font-size: 16px; margin: 5px; }
        """)
        
        layout = QVBoxLayout(container)
        
        fare_title = QLabel("Trip Details")
        fare_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        
        self.distance_label = QLabel("Distance: --")
        self.distance_label.setStyleSheet("color: #3498db;")
        
        self.fare_label = QLabel("Estimated Fare: --")
        self.fare_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        layout.addWidget(fare_title)
        layout.addWidget(self.distance_label)
        layout.addWidget(self.fare_label)
        
        return container
    
    def update_map(self):
        if self.pickup_input.location_data and self.pickup_input.text():
            self.pickup_coords = [
                float(self.pickup_input.location_data[0]['lat']),
                float(self.pickup_input.location_data[0]['lon'])
            ]
            
        if self.dropoff_input.location_data and self.dropoff_input.text():
            self.dropoff_coords = [
                float(self.dropoff_input.location_data[0]['lat']),
                float(self.dropoff_input.location_data[0]['lon'])
            ]
            
        if self.pickup_coords and self.dropoff_coords:
            self.map_view.update_points(self.pickup_coords, self.dropoff_coords)
            self.calculate_fare()
    
    def calculate_fare(self):
        if self.pickup_coords and self.dropoff_coords:
            distance = self.calculate_distance(self.pickup_coords, self.dropoff_coords)
            base_fare = 30.00
            per_km_rate = 5.00
            current_hour = QDateTime.currentDateTime().time().hour()
            time_multiplier = 1.5 if (7 <= current_hour <= 9) or (16 <= current_hour <= 18) else 1.0
            
            self.current_fare = (base_fare + (distance * per_km_rate)) * time_multiplier
            self.distance_label.setText(f"Distance: {distance:.2f} km")
            self.fare_label.setText(f"Estimated Fare: TTD ${self.current_fare:.2f}")
    
    def calculate_distance(self, coord1, coord2):
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        R = 6371  # Earth's radius in kilometers
        distance = R * c
        return distance * 1.2  # Adding 20% for road routes
    
    def show_datetime_picker(self):
        dialog = DateTimePickerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_date = dialog.calendar.selectedDate()
            selected_time = dialog.time_edit.time()
            datetime_str = f"{selected_date.toString('dd/MM/yyyy')} {selected_time.toString('hh:mm AP')}"
            self.datetime_input.setText(datetime_str)
    
    def handle_submit(self):
        if not all([self.pickup_input.text(), self.dropoff_input.text(), self.datetime_input.text()]):
            QMessageBox.warning(self, "Error", "Please fill in all required fields!")
            return
        
        confirm = QMessageBox.question(
            self, "Confirm Booking",
            f"Would you like to confirm this booking?\n\n"
            f"Pickup: {self.pickup_input.text()}\n"
            f"Dropoff: {self.dropoff_input.text()}\n"
            f"Time: {self.datetime_input.text()}\n"
            f"Fare: TTD ${self.current_fare:.2f}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
            
        if confirm == QMessageBox.StandardButton.Yes:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'database', 'taxi_booking.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO bookings (
                        user_id, driver_id, admin_id, pickup_location, dropoff_location, 
                        pickup_time, booking_status, fare, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))
                ''', (
                    current_session.user_id,
                    None,  # driver_id
                    None,  # admin_id
                    self.pickup_input.text(),
                    self.dropoff_input.text(),
                    self.datetime_input.text(),
                    'pending',
                    f"{self.current_fare:.2f}"
                ))
                
                conn.commit()
                QMessageBox.information(self, "Success", "Booking created successfully!")
                self.close()
                
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to create booking: {str(e)}")
            finally:
                conn.close()
