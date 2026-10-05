import sqlite3
import os

DB_NAME = 'f124_championship.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Telemetry Tables ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS circuits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            length_m REAL,
            corners INTEGER,
            drs_zones INTEGER,
            image_url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT,
            circuit_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (circuit_id) REFERENCES circuits (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            driver_id INTEGER,
            lap_number INTEGER,
            lap_time_ms INTEGER,
            sector1_ms INTEGER,
            sector2_ms INTEGER,
            sector3_ms INTEGER,
            is_valid BOOLEAN,
            setup_front_wing INTEGER,
            setup_rear_wing INTEGER,
            session_type_str TEXT,
            tyre_compound TEXT,
            tyre_wear_pct REAL,
            front_left_damage REAL,
            front_right_damage REAL,
            rear_wing_damage REAL,
            weather TEXT,
            track_temperature_c REAL,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
    ''')

    # --- Multi-Season Championship Tables ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_label TEXT NOT NULL,
            is_current BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS season_races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER,
            round_number INTEGER,
            gp_name TEXT,
            circuit_id INTEGER,
            race_date TEXT,
            FOREIGN KEY (season_id) REFERENCES seasons (id),
            FOREIGN KEY (circuit_id) REFERENCES circuits (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hex_color TEXT,
            season_id INTEGER,
            FOREIGN KEY (season_id) REFERENCES seasons (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            car_number INTEGER,
            team_id INTEGER,
            season_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (season_id) REFERENCES seasons (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_race_id INTEGER,
            driver_id INTEGER,
            grid_position INTEGER,
            finish_position INTEGER,
            points_scored INTEGER DEFAULT 0,
            has_fastest_lap BOOLEAN DEFAULT 0,
            is_dnf BOOLEAN DEFAULT 0,
            FOREIGN KEY (season_race_id) REFERENCES season_races (id),
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT,
            year INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_constructor_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT,
            year INTEGER
        )
    ''')

    # --- Seeding ---
    cursor.execute("SELECT COUNT(*) FROM seasons")
    if cursor.fetchone()[0] == 0:
        print("Seeding database with multi-season data and circuit info...")
        
        # Seasons
        cursor.execute("INSERT INTO seasons (year_label, is_current) VALUES (?, ?)", ("2024", True))
        s2024_id = cursor.lastrowid
        cursor.execute("INSERT INTO seasons (year_label, is_current) VALUES (?, ?)", ("2025", False))
        s2025_id = cursor.lastrowid

        # Circuits (with new metadata)
        circuits = [
            ("Bahrain", 5412, 15, 3, "/static/images/circuits/bahrain.svg"),
            ("Saudi Arabia", 6174, 27, 3, "/static/images/circuits/saudi.svg"),
            ("Australia", 5278, 14, 4, "/static/images/circuits/australia.svg")
        ]
        for i, c in enumerate(circuits):
            cursor.execute("INSERT INTO circuits (name, length_m, corners, drs_zones, image_url) VALUES (?, ?, ?, ?, ?)", c)
            c_id = cursor.lastrowid
            cursor.execute("INSERT INTO season_races (season_id, round_number, gp_name, circuit_id) VALUES (?, ?, ?, ?)", 
                           (s2024_id, i+1, f"{c[0]} Grand Prix", c_id))
            
            # Create a mock session for each circuit so telemetry can map to it
            cursor.execute("INSERT INTO sessions (session_type, circuit_id) VALUES (?, ?)", ("Race", c_id))

        # Teams 2024
        teams_data = [
            ("Ferrari", "#E10600", s2024_id),
            ("Mercedes", "#00D2BE", s2024_id),
            ("Red Bull Racing", "#1E41FF", s2024_id),
            ("McLaren", "#FF8700", s2024_id)
        ]
        cursor.executemany("INSERT INTO teams (name, hex_color, season_id) VALUES (?, ?, ?)", teams_data)
        
        # Drivers 2024
        drivers_data = [
            ("Charles Leclerc", 16, 1, s2024_id),
            ("Carlos Sainz", 55, 1, s2024_id),
            ("Lewis Hamilton", 44, 2, s2024_id),
            ("George Russell", 63, 2, s2024_id),
            ("Max Verstappen", 1, 3, s2024_id),
            ("Sergio Perez", 11, 3, s2024_id),
            ("Lando Norris", 4, 4, s2024_id),
            ("Oscar Piastri", 81, 4, s2024_id)
        ]
        cursor.executemany("INSERT INTO drivers (name, car_number, team_id, season_id) VALUES (?, ?, ?, ?)", drivers_data)
        
        # Historical
        driver_titles = [("Michael Schumacher", 2004), ("Lewis Hamilton", 2020), ("Max Verstappen", 2023)]
        cursor.executemany("INSERT INTO historical_titles (driver_name, year) VALUES (?, ?)", driver_titles)
        const_titles = [("Ferrari", 2008), ("Mercedes", 2021), ("Red Bull Racing", 2023)]
        cursor.executemany("INSERT INTO historical_constructor_titles (team_name, year) VALUES (?, ?)", const_titles)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
