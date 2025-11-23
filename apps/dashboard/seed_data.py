import sqlite3
import random
from datetime import datetime, timedelta
import os

import os

# Get absolute path to the project root (2 levels up from this script)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, "farmtech.db")

def connect_db():
    return sqlite3.connect(DB_PATH)

def seed_culturas(conn):
    cursor = conn.cursor()
    culturas = [
        ("Mandioca",),
        ("Cana de Açúcar",),
        ("Milho",),
        ("Soja",),
        ("Café",)
    ]
    
    print("Seeding Culturas...")
    for (nome,) in culturas:
        try:
            cursor.execute("INSERT INTO culturas (nome_cultura) VALUES (?)", (nome,))
        except sqlite3.IntegrityError:
            pass # Already exists
    conn.commit()

def seed_producao(conn):
    cursor = conn.cursor()
    
    # Create table if not exists (since it might be missing from models)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS producao_agricola (
        id_producao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cultura INTEGER NOT NULL,
        quantidade_produzida REAL,
        data_colheita DATETIME,
        valor_estimado REAL,
        area_plantada REAL,
        FOREIGN KEY(id_cultura) REFERENCES culturas(id_cultura)
    )
    """)
    
    cursor.execute("SELECT id_cultura FROM culturas")
    cultura_ids = [row[0] for row in cursor.fetchall()]
    
    if not cultura_ids:
        print("No culturas found!")
        return

    print("Seeding Producao...")
    # Generate data for last 3 years
    start_date = datetime.now() - timedelta(days=365*3)
    
    for _ in range(50): # 50 production records
        cultura_id = random.choice(cultura_ids)
        area = random.uniform(5, 100) # hectares
        prod_ton = area * random.uniform(10, 80) # tons
        data_colheita = start_date + timedelta(days=random.randint(0, 365*3))
        valor = prod_ton * random.uniform(500, 2000) # Reais per ton
        
        cursor.execute("""
            INSERT INTO producao_agricola 
            (id_cultura, quantidade_produzida, data_colheita, valor_estimado, area_plantada) 
            VALUES (?, ?, ?, ?, ?)
        """, (cultura_id, prod_ton, data_colheita, valor, area))
    conn.commit()

def seed_leituras(conn):
    cursor = conn.cursor()
    # Ensure sensor exists
    cursor.execute("SELECT id_sensor FROM sensores LIMIT 1")
    res = cursor.fetchone()
    if not res:
        print("No sensor found. Creating one...")
        # Create dummy talhao and sensor if needed (simplified)
        cursor.execute("INSERT OR IGNORE INTO talhoes (nome_talhao, area_hectares) VALUES ('Talhão Demo', 50)")
        talhao_id = cursor.lastrowid or 1
        cursor.execute("INSERT OR IGNORE INTO tipos_sensor (nome_tipo_sensor, unidade_medida_padrao) VALUES ('Multisensor', 'Mix')")
        tipo_id = cursor.lastrowid or 1
        cursor.execute("INSERT INTO sensores (identificacao_fabricante, data_instalacao, id_tipo_sensor, id_talhao) VALUES ('ESP32-SEED', ?, ?, ?)", (datetime.now().date(), tipo_id, talhao_id))
        sensor_id = cursor.lastrowid
    else:
        sensor_id = res[0]

    print("Seeding Leituras (IoT)...")
    # Generate 1000 readings over last week
    end_date = datetime.now()
    
    readings = []
    for i in range(1000):
        timestamp = end_date - timedelta(minutes=10*i)
        
        # Simulate daily cycle for temp/humidity
        hour = timestamp.hour
        is_day = 6 <= hour <= 18
        
        temp_base = 25 if is_day else 18
        temp = temp_base + random.uniform(-2, 5)
        
        hum_base = 60 if is_day else 80
        hum = hum_base + random.uniform(-10, 10)
        
        ph = random.uniform(5.5, 7.0)
        
        # Logic simulation
        bomba = hum < 30
        decisao = "Irrigar" if bomba else "Monitorar"
        
        readings.append((
            sensor_id, hum, ph, temp, 1.0, 1.0, bomba, decisao, timestamp
        ))
    
    cursor.executemany("""
        INSERT INTO leituras_sensores 
        (id_sensor, valor_umidade, valor_ph, temperatura, valor_fosforo_p, valor_potassio_k, bomba_ligada, decisao_logica_esp32, data_hora_leitura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, readings)
    conn.commit()

def seed_deteccoes(conn):
    cursor = conn.cursor()
    print("Seeding Deteccoes (CV)...")
    
    classes = ["Broca-do-cafe", "Lagarta-do-cartucho", "Ferrugem-asiatica", "Saudavel"]
    
    detections = []
    for _ in range(100):
        cls = random.choice(classes)
        conf = random.uniform(0.7, 0.99)
        ts = datetime.now() - timedelta(hours=random.randint(0, 48))
        img_name = f"cam1_{ts.strftime('%Y%m%d_%H%M%S')}.jpg"
        bbox = f"[{random.randint(0,500)}, {random.randint(0,500)}, {random.randint(500,1000)}, {random.randint(500,1000)}]"
        
        detections.append((ts, img_name, cls, conf, bbox))
        
    cursor.executemany("""
        INSERT INTO deteccoes (timestamp, imagem_nome, classe, confianca, bbox)
        VALUES (?, ?, ?, ?, ?)
    """, detections)
    conn.commit()

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
    else:
        conn = connect_db()
        try:
            seed_culturas(conn)
            seed_producao(conn)
            seed_leituras(conn)
            seed_deteccoes(conn)
            print("Seeding complete!")
        except Exception as e:
            print(f"Error seeding: {e}")
        finally:
            conn.close()
