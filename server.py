from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import database
import json
import asyncio
import struct

app = FastAPI(title="F1 24 Telemetry & Championship API")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

UDP_IP = "0.0.0.0"
UDP_PORT = 20777

# --- Memory State ---
CURRENT_SESSION_STATE = {
    "weather": "Unknown",
    "track_temperature_c": 0.0,
    "session_type_str": "Unknown",
    "cars": {} # car_index -> { "driver_id": 0, "tyre_compound": "", "wear": 0.0, "fl_damage": 0.0, "fr_damage": 0.0, "rw_damage": 0.0 }
}

class UDPServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        print(f"UDP server listening on {UDP_PORT}")

    def datagram_received(self, data, addr):
        if len(data) >= 29:
            try:
                packet_format = '<HBBBBQfI2B'
                header_data = struct.unpack_from(packet_format, data, 0)
                packet_id = header_data[4]
            except Exception as e:
                pass

async def start_udp_listener():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=(UDP_IP, UDP_PORT)
    )

@app.on_event("startup")
async def startup_event():
    database.init_db()
    asyncio.create_task(start_udp_listener())

# --- Models ---
class SeasonCreate(BaseModel):
    year_label: str
    is_current: bool = False

class DriverCreate(BaseModel):
    name: str
    car_number: int
    team_id: Optional[int] = None
    season_id: int

class TeamCreate(BaseModel):
    name: str
    hex_color: Optional[str] = None
    season_id: int

class RaceResultItem(BaseModel):
    driver_id: int
    grid_position: int
    finish_position: int
    has_fastest_lap: bool = False
    is_dnf: bool = False

class RaceResultBatch(BaseModel):
    season_race_id: int
    results: List[RaceResultItem]

class LapCreate(BaseModel):
    session_id: int
    driver_id: int
    lap_number: int
    lap_time_ms: int
    is_valid: bool = True
    sector1_ms: Optional[int] = None
    sector2_ms: Optional[int] = None
    sector3_ms: Optional[int] = None
    session_type_str: Optional[str] = None
    tyre_compound: Optional[str] = None
    tyre_wear_pct: Optional[float] = None
    front_left_damage: Optional[float] = None
    front_right_damage: Optional[float] = None
    rear_wing_damage: Optional[float] = None
    weather: Optional[str] = None
    track_temperature_c: Optional[float] = None

# --- Endpoints ---

@app.post("/api/telemetry/submit")
def submit_telemetry(lap: LapCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO laps (session_id, driver_id, lap_number, lap_time_ms, sector1_ms, sector2_ms, sector3_ms, is_valid, session_type_str, tyre_compound, tyre_wear_pct, front_left_damage, front_right_damage, rear_wing_damage, weather, track_temperature_c)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lap.session_id, lap.driver_id, lap.lap_number, lap.lap_time_ms, lap.sector1_ms, lap.sector2_ms, lap.sector3_ms, lap.is_valid, lap.session_type_str, lap.tyre_compound, lap.tyre_wear_pct, lap.front_left_damage, lap.front_right_damage, lap.rear_wing_damage, lap.weather, lap.track_temperature_c))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Telemetry saved"}

# Seasons
@app.get("/api/seasons")
def get_seasons():
    conn = database.get_db_connection()
    seasons = conn.execute("SELECT * FROM seasons ORDER BY year_label DESC").fetchall()
    conn.close()
    return [dict(ix) for ix in seasons]

@app.post("/api/seasons")
def create_season(season: SeasonCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO seasons (year_label, is_current) VALUES (?, ?)", (season.year_label, season.is_current))
    conn.commit()
    season_id = cursor.lastrowid
    conn.close()
    return {"id": season_id, "status": "success"}

# Races for a Season
@app.get("/api/seasons/{season_id}/races")
def get_season_races(season_id: int):
    conn = database.get_db_connection()
    races = conn.execute("SELECT sr.*, c.name as circuit_name FROM season_races sr JOIN circuits c ON sr.circuit_id = c.id WHERE sr.season_id = ? ORDER BY sr.round_number ASC", (season_id,)).fetchall()
    conn.close()
    return [dict(ix) for ix in races]

# Drivers
@app.get("/drivers/")
def get_drivers(season_id: int = None):
    conn = database.get_db_connection()
    if season_id:
        drivers = conn.execute("SELECT * FROM drivers WHERE season_id = ?", (season_id,)).fetchall()
    else:
        drivers = conn.execute("SELECT * FROM drivers").fetchall()
    conn.close()
    return [dict(ix) for ix in drivers]

@app.post("/drivers/")
def create_driver(driver: DriverCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO drivers (name, car_number, team_id, season_id) VALUES (?, ?, ?, ?)", 
                   (driver.name, driver.car_number, driver.team_id, driver.season_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

# Teams
@app.get("/teams/")
def get_teams(season_id: int = None):
    conn = database.get_db_connection()
    if season_id:
        teams = conn.execute("SELECT * FROM teams WHERE season_id = ?", (season_id,)).fetchall()
    else:
        teams = conn.execute("SELECT * FROM teams").fetchall()
    conn.close()
    return [dict(ix) for ix in teams]

# Race Results
@app.post("/race_results/batch")
def add_race_results(batch: RaceResultBatch):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    points_map = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
    for res in batch.results:
        pts = points_map.get(res.finish_position, 0)
        if res.has_fastest_lap and res.finish_position <= 10 and not res.is_dnf:
            pts += 1
        
        # Upsert logic - delete existing for this driver in this race
        cursor.execute("DELETE FROM race_results WHERE season_race_id = ? AND driver_id = ?", (batch.season_race_id, res.driver_id))
        
        cursor.execute('''
            INSERT INTO race_results (season_race_id, driver_id, grid_position, finish_position, points_scored, has_fastest_lap, is_dnf)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (batch.season_race_id, res.driver_id, res.grid_position, res.finish_position, pts, res.has_fastest_lap, res.is_dnf))
    conn.commit()
    conn.close()
    return {"status": "success"}

# Standings
@app.get("/standings/drivers")
def get_driver_standings(season_id: int):
    conn = database.get_db_connection()
    query = '''
        SELECT d.id, d.name, d.car_number, t.name as team_name, t.hex_color,
               SUM(r.points_scored) as total_points,
               SUM(CASE WHEN r.finish_position = 1 AND r.is_dnf = 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN r.finish_position <= 3 AND r.is_dnf = 0 THEN 1 ELSE 0 END) as podiums
        FROM drivers d
        LEFT JOIN teams t ON d.team_id = t.id
        LEFT JOIN race_results r ON d.id = r.driver_id
        WHERE d.season_id = ?
        GROUP BY d.id
        ORDER BY total_points DESC, wins DESC
    '''
    standings = conn.execute(query, (season_id,)).fetchall()
    conn.close()
    return [dict(ix) for ix in standings]

@app.get("/standings/constructors")
def get_constructor_standings(season_id: int):
    conn = database.get_db_connection()
    query = '''
        SELECT t.id, t.name, t.hex_color,
               SUM(r.points_scored) as total_points,
               SUM(CASE WHEN r.finish_position = 1 AND r.is_dnf = 0 THEN 1 ELSE 0 END) as wins
        FROM teams t
        LEFT JOIN drivers d ON t.id = d.team_id
        LEFT JOIN race_results r ON d.id = r.driver_id
        WHERE t.season_id = ?
        GROUP BY t.id
        ORDER BY total_points DESC, wins DESC
    '''
    standings = conn.execute(query, (season_id,)).fetchall()
    conn.close()
    return [dict(ix) for ix in standings]

# Hall of Fame
@app.get("/hall_of_fame/drivers")
def get_hof_drivers():
    conn = database.get_db_connection()
    query = '''
        SELECT driver_name as name, COUNT(id) as titles, GROUP_CONCAT(year) as years
        FROM historical_titles
        GROUP BY driver_name
        ORDER BY titles DESC
    '''
    hof = conn.execute(query).fetchall()
    conn.close()
    res = []
    for r in hof:
        d = dict(r)
        d['years'] = [int(y) for y in d['years'].split(',')] if d['years'] else []
        res.append(d)
    return res

@app.get("/hall_of_fame/constructors")
def get_hof_constructors():
    conn = database.get_db_connection()
    query = '''
        SELECT team_name as name, COUNT(id) as titles, GROUP_CONCAT(year) as years
        FROM historical_constructor_titles
        GROUP BY team_name
        ORDER BY titles DESC
    '''
    hof = conn.execute(query).fetchall()
    conn.close()
    res = []
    for r in hof:
        d = dict(r)
        d['years'] = [int(y) for y in d['years'].split(',')] if d['years'] else []
        res.append(d)
    return res

@app.get("/api/seasons/{season_id}/progression")
def get_season_progression(season_id: int):
    conn = database.get_db_connection()
    
    # Get all races for season ordered by round
    races = conn.execute("SELECT id, round_number, gp_name FROM season_races WHERE season_id = ? ORDER BY round_number", (season_id,)).fetchall()
    race_labels = [r['gp_name'] for r in races]
    
    # Get all drivers in season
    drivers = conn.execute("SELECT d.id, d.name, t.hex_color FROM drivers d JOIN teams t ON d.team_id = t.id WHERE d.season_id = ?", (season_id,)).fetchall()
    
    datasets = []
    for d in drivers:
        d_id = d['id']
        # Get points scored per race
        points_query = '''
            SELECT sr.round_number, COALESCE(r.points_scored, 0) as pts
            FROM season_races sr
            LEFT JOIN race_results r ON sr.id = r.season_race_id AND r.driver_id = ?
            WHERE sr.season_id = ?
            ORDER BY sr.round_number
        '''
        results = conn.execute(points_query, (d_id, season_id)).fetchall()
        
        cumulative = []
        total = 0
        for res in results:
            total += res['pts']
            cumulative.append(total)
            
        datasets.append({
            "label": d['name'],
            "data": cumulative,
            "borderColor": d['hex_color'],
            "backgroundColor": d['hex_color'],
            "tension": 0.4,
            "fill": False
        })
        
    conn.close()
    return {"labels": race_labels, "datasets": datasets}

# Export
@app.get("/export")
def export_db():
    conn = database.get_db_connection()
    tables = ['seasons', 'season_races', 'teams', 'drivers', 'historical_titles', 'historical_constructor_titles', 'circuits', 'sessions', 'laps', 'race_results']
    db_dump = {}
    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        db_dump[table] = [dict(ix) for ix in rows]
    conn.close()
    return db_dump

# Laps
@app.get("/laps/")
def get_laps(driver_id: Optional[int] = None, circuit_id: Optional[int] = None):
    conn = database.get_db_connection()
    query = 'SELECT l.* FROM laps l'
    params = []
    
    if circuit_id:
        query += ' JOIN sessions s ON l.session_id = s.id WHERE s.circuit_id = ?'
        params.append(circuit_id)
        if driver_id:
            query += ' AND l.driver_id = ?'
            params.append(driver_id)
    else:
        if driver_id:
            query += ' WHERE l.driver_id = ?'
            params.append(driver_id)
            
    laps = conn.execute(query, params).fetchall()
    
    ideal = 0
    if driver_id and circuit_id:
        best_s1 = conn.execute('SELECT MIN(l.sector1_ms) as ms FROM laps l JOIN sessions s ON l.session_id = s.id WHERE l.driver_id = ? AND s.circuit_id = ? AND l.is_valid = 1 AND l.sector1_ms > 0', (driver_id, circuit_id)).fetchone()
        best_s2 = conn.execute('SELECT MIN(l.sector2_ms) as ms FROM laps l JOIN sessions s ON l.session_id = s.id WHERE l.driver_id = ? AND s.circuit_id = ? AND l.is_valid = 1 AND l.sector2_ms > 0', (driver_id, circuit_id)).fetchone()
        best_s3 = conn.execute('SELECT MIN(l.sector3_ms) as ms FROM laps l JOIN sessions s ON l.session_id = s.id WHERE l.driver_id = ? AND s.circuit_id = ? AND l.is_valid = 1 AND l.sector3_ms > 0', (driver_id, circuit_id)).fetchone()
        ideal = (best_s1['ms'] or 0) + (best_s2['ms'] or 0) + (best_s3['ms'] or 0)

    conn.close()
    return {"laps": [dict(ix) for ix in laps], "ideal_lap_ms": ideal}

# Circuits & Leaderboard
@app.get("/api/circuits")
def get_circuits():
    conn = database.get_db_connection()
    circuits = conn.execute("SELECT * FROM circuits").fetchall()
    conn.close()
    return [dict(ix) for ix in circuits]

@app.get("/api/circuits/{circuit_id}/leaderboard")
def get_circuit_leaderboard(circuit_id: int):
    conn = database.get_db_connection()
    
    # Absolute best lap
    best_lap = conn.execute('''
        SELECT l.lap_time_ms as ms, d.name, d.car_number, t.hex_color 
        FROM laps l JOIN sessions s ON l.session_id = s.id JOIN drivers d ON l.driver_id = d.id LEFT JOIN teams t ON d.team_id = t.id
        WHERE s.circuit_id = ? AND l.is_valid = 1 AND l.lap_time_ms > 0
        ORDER BY l.lap_time_ms ASC LIMIT 1
    ''', (circuit_id,)).fetchone()
    
    # Best S1
    best_s1 = conn.execute('''
        SELECT l.sector1_ms as ms, d.name 
        FROM laps l JOIN sessions s ON l.session_id = s.id JOIN drivers d ON l.driver_id = d.id
        WHERE s.circuit_id = ? AND l.is_valid = 1 AND l.sector1_ms > 0
        ORDER BY l.sector1_ms ASC LIMIT 1
    ''', (circuit_id,)).fetchone()
    
    # Best S2
    best_s2 = conn.execute('''
        SELECT l.sector2_ms as ms, d.name 
        FROM laps l JOIN sessions s ON l.session_id = s.id JOIN drivers d ON l.driver_id = d.id
        WHERE s.circuit_id = ? AND l.is_valid = 1 AND l.sector2_ms > 0
        ORDER BY l.sector2_ms ASC LIMIT 1
    ''', (circuit_id,)).fetchone()
    
    # Best S3
    best_s3 = conn.execute('''
        SELECT l.sector3_ms as ms, d.name 
        FROM laps l JOIN sessions s ON l.session_id = s.id JOIN drivers d ON l.driver_id = d.id
        WHERE s.circuit_id = ? AND l.is_valid = 1 AND l.sector3_ms > 0
        ORDER BY l.sector3_ms ASC LIMIT 1
    ''', (circuit_id,)).fetchone()
    
    conn.close()
    
    return {
        "best_lap": dict(best_lap) if best_lap else None,
        "s1": dict(best_s1) if best_s1 else None,
        "s2": dict(best_s2) if best_s2 else None,
        "s3": dict(best_s3) if best_s3 else None
    }
