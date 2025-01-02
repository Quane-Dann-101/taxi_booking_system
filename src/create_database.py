import sqlite3
import os

def create_database():
    # Get absolute path to database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'taxi_booking.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create drivers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        car_model TEXT NOT NULL,
        license_plate TEXT UNIQUE NOT NULL,
        driver_license TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'available',
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create admins table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        full_name TEXT NOT NULL,
        access_level TEXT DEFAULT 'standard',
        last_login DATETIME
    )
    ''')

    # Create bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        driver_id INTEGER,
        admin_id INTEGER,
        pickup_location TEXT NOT NULL,
        dropoff_location TEXT NOT NULL,
        pickup_time DATETIME NOT NULL,
        booking_status TEXT DEFAULT 'pending',
        fare DECIMAL(10,2),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (driver_id) REFERENCES drivers(id),
        FOREIGN KEY (admin_id) REFERENCES admins(id)
    )
    ''')

    
    conn.commit()
    conn.close()
    print("Database created successfully with all tables!")

if __name__ == "__main__":
    create_database()
