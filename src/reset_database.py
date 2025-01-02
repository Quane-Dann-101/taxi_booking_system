import sqlite3
import os

def reset_database():
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'taxi_booking.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    
    # Clear all tables
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM drivers')
    cursor.execute('DELETE FROM admins')
    cursor.execute('DELETE FROM bookings')

    # Reset auto-increment counters
    cursor.execute('DELETE FROM sqlite_sequence')

    # Sample test data
    test_users = [
        ('user1', 'pass1', 'user1@test.com', '(868) 555-0001', '123 Main St'),
        ('user2', 'pass1', 'user2@test.com', '(868) 555-0002', '456 Oak Ave')
    ]

    test_drivers = [
        ('driver1', 'Password123!', 'driver1@test.com', '(868) 555-0004', 'Toyota Camry', 'ABC123', 'John Driver'),
        ('driver2', 'Password123!', 'driver2@test.com', '(868) 555-0005', 'Honda Civic', 'XYZ789', 'Jane Driver'),
        ('driver3', 'Password123!', 'driver3@test.com', '(868) 555-0006', 'Ford Focus', 'DEF456', 'Bob Driver')
    ]

    test_admins = [
        ('admin1', 'Password123!', 'admin1@test.com', '(868) 555-0007', 'System Admin'),
        ('admin2', 'Password123!', 'admin2@test.com', '(868) 555-0008', 'Support Admin')
    ]
    

    # Insert test data
    cursor.executemany('INSERT INTO users (username, password, email, phone, address) VALUES (?, ?, ?, ?, ?)', test_users)
    cursor.executemany('INSERT INTO drivers (username, password, email, phone, car_model, license_plate, full_name) VALUES (?, ?, ?, ?, ?, ?, ?)', test_drivers)
    cursor.executemany('INSERT INTO admins (username, password, email, phone, full_name) VALUES (?, ?, ?, ?, ?)', test_admins)

    conn.commit()
    conn.close()
    print("Database reset completed! Test data inserted successfully.")

if __name__ == "__main__":
    reset_database()
