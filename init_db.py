"""
FurnitureFlow – Veritabanı Kurulum / Güncelleme Scripti
    python init_db.py
"""
import sqlite3, hashlib

DB = "furnitureflow.db"

def sha256(pw): return hashlib.sha256(pw.encode()).hexdigest()

def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS collections (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS pieces (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            name          TEXT NOT NULL,
            width_cm      REAL DEFAULT 0,
            depth_cm      REAL DEFAULT 0,
            height_cm     REAL DEFAULT 0,
            loading_order INTEGER DEFAULT 1,
            notes         TEXT DEFAULT '',
            FOREIGN KEY (collection_id) REFERENCES collections(id)
        );
        CREATE TABLE IF NOT EXISTS piece_stock (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            piece_id   INTEGER NOT NULL UNIQUE,
            status     TEXT DEFAULT 'available',
            note       TEXT DEFAULT '',
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (piece_id) REFERENCES pieces(id)
        );
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'personel',
            full_name     TEXT DEFAULT '',
            is_active     INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number    TEXT NOT NULL UNIQUE,
            collection_id   INTEGER NOT NULL,
            status          TEXT DEFAULT 'pending',
            priority        TEXT DEFAULT 'normal',
            customer_name   TEXT DEFAULT '',
            customer_email  TEXT DEFAULT '',
            customer_phone  TEXT DEFAULT '',
            created_by      TEXT DEFAULT '',
            assigned_to     TEXT DEFAULT '',
            sla_minutes     INTEGER DEFAULT 90,
            created_at      TEXT DEFAULT (datetime('now','localtime')),
            started_at      TEXT,
            completed_at    TEXT,
            notes           TEXT DEFAULT '',
            FOREIGN KEY (collection_id) REFERENCES collections(id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL,
            piece_id    INTEGER NOT NULL,
            is_checked  INTEGER DEFAULT 0,
            item_status TEXT DEFAULT 'normal',
            item_note   TEXT DEFAULT '',
            checked_at  TEXT,
            FOREIGN KEY (order_id)  REFERENCES orders(id),
            FOREIGN KEY (piece_id)  REFERENCES pieces(id)
        );
        CREATE TABLE IF NOT EXISTS vehicle_types (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            capacity_m3 REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS customer_tokens (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   INTEGER NOT NULL UNIQUE,
            token      TEXT NOT NULL UNIQUE,
            viewed_at  TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            type       TEXT NOT NULL,
            message    TEXT NOT NULL,
            order_id   INTEGER,
            is_read    INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS sla_config (
            collection_id INTEGER NOT NULL UNIQUE,
            sla_minutes   INTEGER NOT NULL DEFAULT 90,
            FOREIGN KEY (collection_id) REFERENCES collections(id)
        );
        CREATE TABLE IF NOT EXISTS app_settings (
            key   TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            action     TEXT NOT NULL,
            entity     TEXT NOT NULL,
            entity_id  TEXT,
            detail     TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS deliveries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     INTEGER NOT NULL UNIQUE,
            address      TEXT DEFAULT '',
            district     TEXT DEFAULT '',
            city         TEXT DEFAULT 'Bursa',
            lat          REAL DEFAULT 0,
            lng          REAL DEFAULT 0,
            delivery_date TEXT DEFAULT (DATE('now')),
            time_window  TEXT DEFAULT '09:00-18:00',
            status       TEXT DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS route_plans (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_date    TEXT NOT NULL,
            vehicle_name TEXT DEFAULT '',
            stop_order   TEXT DEFAULT '',
            total_km_est REAL DEFAULT 0,
            created_by   TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()
    print("✅ Tablolar oluşturuldu.")

def migrate(conn):
    c = conn.cursor()
    cols = [
        ("orders","priority",      "TEXT DEFAULT 'normal'"),
        ("orders","customer_phone","TEXT DEFAULT ''"),
        ("orders","assigned_to",   "TEXT DEFAULT ''"),
        ("orders","sla_minutes",   "INTEGER DEFAULT 90"),
        ("orders","started_at",    "TEXT"),
        ("orders","notes",         "TEXT DEFAULT ''"),
        ("order_items","item_status","TEXT DEFAULT 'normal'"),
        ("order_items","item_note",  "TEXT DEFAULT ''"),
        ("orders","customer_email",  "TEXT DEFAULT ''"),
        ("orders","created_by",      "TEXT DEFAULT ''"),
    ]
    for table, col, defn in cols:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
        except Exception:
            pass
    # Create new tables if missing (for existing DBs)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            action     TEXT NOT NULL,
            entity     TEXT NOT NULL,
            entity_id  TEXT,
            detail     TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS deliveries (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER NOT NULL UNIQUE,
            address       TEXT DEFAULT '',
            district      TEXT DEFAULT '',
            city          TEXT DEFAULT 'Bursa',
            lat           REAL DEFAULT 0,
            lng           REAL DEFAULT 0,
            delivery_date TEXT DEFAULT (DATE('now')),
            time_window   TEXT DEFAULT '09:00-18:00',
            status        TEXT DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS route_plans (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_date    TEXT NOT NULL,
            vehicle_name TEXT DEFAULT '',
            stop_order   TEXT DEFAULT '',
            total_km_est REAL DEFAULT 0,
            created_by   TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()

    # Parça adlarını Türkçeye güncelle (mevcut DB için)
    rename_map = {
        "Dining Table":                     "Yemek Masası",
        "Dining Table Standard":            "Yemek Masası (Standart)",
        "Dining Table Little Size":         "Yemek Masası (Küçük Boy)",
        "TV Unit":                          "TV Ünitesi",
        "Sideboard":                        "Konsol",
        "4 Seater Sofa":                    "4'lü Koltuk",
        "3.5 Seater Sofa":                  "3,5'li Koltuk",
        "3 Seater Sofa":                    "3'lü Koltuk",
        "3 Seater Sofa F1":                 "3'lü Koltuk F1",
        "2 Seater Sofa":                    "2'li Koltuk",
        "1 Seater Sofa":                    "Tekli Koltuk",
        "Armchair":                         "Berjer",
        "Angel Armchair":                   "Angel Berjer",
        "Bench":                            "Puf Sedir",
        "Chair":                            "Sandalye",
        "Coffee Table":                     "Orta Sehpa",
        "Coffee Table Large":               "Orta Sehpa (Büyük)",
        "Coffee Table Small":               "Orta Sehpa (Küçük)",
        "Nesting Table":                    "Zigon Sehpa",
        "Nesting Table Large":              "Zigon Sehpa (Büyük)",
        "Nesting Table Small":              "Zigon Sehpa (Küçük)",
        "Side Table":                       "Yan Sehpa",
        "Dresser":                          "Şifonyer",
        "Resting Corner":                   "Dinlenme Köşesi",
        "Mirror":                           "Ayna",
        "4 Seater Sofa (272 cm)":           "4'lü Koltuk (272 cm)",
        "4 Seater Sofa (285 cm)":           "4'lü Koltuk (285 cm)",
        "4 Seater Sofa (295 cm)":           "4'lü Koltuk (295 cm)",
        "3 Seater Sofa w/ MP Coffee Table": "3'lü Koltuk (Orta Sehpalı)",
        "3 Seater Sofa (242 cm)":           "3'lü Koltuk (242 cm)",
        "3 Seater Sofa (255 cm)":           "3'lü Koltuk (255 cm)",
        "3 Seater Sofa (235 cm)":           "3'lü Koltuk (235 cm)",
        "3 Seater Sofa (242cm)":            "3'lü Koltuk (242 cm)",
        "3.5 Seater Sofa (255cm)":          "3,5'li Koltuk (255 cm)",
        "2 Seater Sofa (212 cm)":           "2'li Koltuk (212 cm)",
        "2 Seater Sofa (225 cm)":           "2'li Koltuk (225 cm)",
    }
    renamed = 0
    for eng, tr in rename_map.items():
        r = conn.execute("UPDATE pieces SET name=? WHERE name=?", (tr, eng))
        renamed += r.rowcount
    conn.commit()
    if renamed > 0:
        print(f"  🔤 {renamed} parça adı Türkçeye çevrildi.")

def insert_defaults(conn):
    users = [
        ("admin",    sha256("admin123"),    "admin",    "Sistem Yöneticisi"),
        ("yonetici", sha256("yonetici123"), "yonetici", "Depo Yöneticisi"),
        ("personel", sha256("personel123"), "personel", "Depo Personeli"),
        ("personel2",sha256("personel123"), "personel", "Depo Personeli 2"),
    ]
    for u in users:
        conn.execute("INSERT OR IGNORE INTO users (username,password_hash,role,full_name) VALUES(?,?,?,?)", u)

    vehicles = [("TIR",90.0),("Büyük Kamyon",50.0),("Orta Kamyon",30.0),("Minivan",10.0)]
    for v in vehicles:
        conn.execute("INSERT OR IGNORE INTO vehicle_types (name,capacity_m3) VALUES(?,?)", v)

    settings = [
        ("smtp_host",   "smtp.gmail.com"),
        ("smtp_port",   "587"),
        ("smtp_user",   ""),
        ("smtp_pass",   ""),
        ("company_name","Luxe Life Mobilya"),
        ("app_url",     "http://localhost:8501"),
    ]
    for s in settings:
        conn.execute("INSERT OR IGNORE INTO app_settings (key,value) VALUES(?,?)", s)

    conn.commit()
    print("✅ Kullanıcılar, araçlar, ayarlar eklendi.")

def insert_furniture(conn):
    colls = ["AURA","BELEZZA","BRAGA","FENDI","HILTON","MASSIMO","NOBEL","OSCAR","PORTO"]
    for n in colls:
        conn.execute("INSERT OR IGNORE INTO collections (name) VALUES(?)", (n,))
    conn.commit()

    rows = conn.execute("SELECT id,name FROM collections").fetchall()
    cmap = {n: i for i,n in rows}

    # Önce tüm duplicate parçaları temizle (her koleksiyon+isim kombinasyonu için
    # en küçük id'li olanı koru)
    conn.execute("""
        DELETE FROM pieces
        WHERE id NOT IN (
            SELECT MIN(id) FROM pieces GROUP BY collection_id, name
        )
    """)
    conn.commit()

    # Ardından eksik parçaları ekle — mevcut olanları atla (INSERT OR IGNORE için
    # geçici UNIQUE constraint yerine Python'da kontrol ederiz)
    existing = {
        (r["collection_id"], r["name"])
        for r in conn.execute("SELECT collection_id, name FROM pieces").fetchall()
    }

    pieces = [
        # AURA
        ("AURA","Yemek Masası",230,115,78,1),
        ("AURA","TV Ünitesi",300,50,52,2),
        ("AURA","Konsol",230,50,118,3),
        ("AURA","4'lü Koltuk",290,100,100,4),
        ("AURA","3,5'li Koltuk",260,100,100,5),
        ("AURA","3'lü Koltuk",240,100,100,6),
        ("AURA","2'li Koltuk",200,100,100,7),
        ("AURA","Berjer",92,90,75,8),
        ("AURA","Puf Sedir",170,50,46,9),
        ("AURA","Orta Sehpa",104,75,42,10),
        ("AURA","Sandalye",57,56,87,11),
        ("AURA","Zigon Sehpa",60,55,59,12),
        # BELEZZA
        ("BELEZZA","Yemek Masası (Standart)",220,98,76,1),
        ("BELEZZA","Yemek Masası (Küçük Boy)",180,98,76,2),
        ("BELEZZA","Konsol",229,45,120,3),
        ("BELEZZA","TV Ünitesi",220,45,60,4),
        ("BELEZZA","4'lü Koltuk",290,100,100,5),
        ("BELEZZA","3'lü Koltuk",260,100,100,6),
        ("BELEZZA","2'li Koltuk",230,100,100,7),
        ("BELEZZA","Berjer",80,82,87,8),
        ("BELEZZA","Şifonyer",130,45,90,9),
        ("BELEZZA","Orta Sehpa",90,128,30,10),
        ("BELEZZA","Yan Sehpa",60,60,60,11),
        ("BELEZZA","Zigon Sehpa",50,50,60,12),
        # BRAGA
        ("BRAGA","Yemek Masası",220,100,78,1),
        ("BRAGA","Konsol",228,45,92,2),
        ("BRAGA","TV Ünitesi",228,50,60,3),
        ("BRAGA","4'lü Koltuk",290,96,96,4),
        ("BRAGA","3'lü Koltuk",250,96,96,5),
        ("BRAGA","2'li Koltuk",210,96,96,6),
        ("BRAGA","Berjer",75,79,82,7),
        ("BRAGA","Şifonyer",130,40,79,8),
        ("BRAGA","Orta Sehpa (Büyük)",90,90,40,9),
        ("BRAGA","Orta Sehpa (Küçük)",70,70,36,10),
        ("BRAGA","Zigon Sehpa (Büyük)",55,55,69,11),
        ("BRAGA","Zigon Sehpa (Küçük)",55,55,55,12),
        # FENDI
        ("FENDI","Yemek Masası (Standart)",220,100,76,1),
        ("FENDI","Konsol",225,50,118,2),
        ("FENDI","TV Ünitesi",223,45,61,3),
        ("FENDI","3'lü Koltuk",249,94,94,4),
        ("FENDI","2'li Koltuk",197,95,95,5),
        ("FENDI","Berjer",75,62,79,6),
        ("FENDI","Angel Berjer",80,82,73,7),
        ("FENDI","Şifonyer",124,45,92,8),
        ("FENDI","Yan Sehpa",69,45,35,9),
        ("FENDI","Orta Sehpa",90,45,45,10),
        # HILTON
        ("HILTON","Yemek Masası",220,100,79,1),
        ("HILTON","Konsol",220,45,98,2),
        ("HILTON","TV Ünitesi",220,50,62,3),
        ("HILTON","4'lü Koltuk",275,102,102,4),
        ("HILTON","3'lü Koltuk",245,102,102,5),
        ("HILTON","3'lü Koltuk F1",245,102,102,6),
        ("HILTON","2'li Koltuk",215,102,102,7),
        ("HILTON","Berjer",86,90,75,8),
        ("HILTON","Orta Sehpa (Büyük)",100,100,43,9),
        ("HILTON","Orta Sehpa (Küçük)",68,68,34,10),
        ("HILTON","Zigon Sehpa (Büyük)",45,55,49,11),
        ("HILTON","Zigon Sehpa (Küçük)",45,60,60,12),
        # MASSIMO
        ("MASSIMO","Yemek Masası",220,100,78,1),
        ("MASSIMO","Konsol",220,50,100,2),
        ("MASSIMO","TV Ünitesi",220,50,58,3),
        ("MASSIMO","4'lü Koltuk (272 cm)",272,93,93,4),
        ("MASSIMO","3'lü Koltuk (Orta Sehpalı)",282,93,93,5),
        ("MASSIMO","3'lü Koltuk (242 cm)",242,93,93,6),
        ("MASSIMO","2'li Koltuk (212 cm)",212,93,93,7),
        ("MASSIMO","Berjer",87,83,83,8),
        ("MASSIMO","Puf Sedir",165,47,50,9),
        ("MASSIMO","Orta Sehpa (Büyük)",150,80,34,10),
        ("MASSIMO","Orta Sehpa (Küçük)",130,40,39,11),
        ("MASSIMO","Zigon Sehpa (Büyük)",50,50,54,12),
        ("MASSIMO","Zigon Sehpa (Küçük)",60,35,60,13),
        # NOBEL
        ("NOBEL","Yemek Masası",220,50,79,1),
        ("NOBEL","Konsol",220,50,87,2),
        ("NOBEL","TV Ünitesi",220,50,61,3),
        ("NOBEL","4'lü Koltuk (285 cm)",285,93,93,4),
        ("NOBEL","3'lü Koltuk (Orta Sehpalı)",295,93,93,5),
        ("NOBEL","3'lü Koltuk (255 cm)",255,93,93,6),
        ("NOBEL","2'li Koltuk (225 cm)",225,93,93,7),
        ("NOBEL","Berjer",92,81,71,8),
        ("NOBEL","Puf Sedir",172,50,51,9),
        ("NOBEL","Orta Sehpa",120,60,39,10),
        ("NOBEL","Zigon Sehpa (Büyük)",50,50,53,11),
        ("NOBEL","Zigon Sehpa (Küçük)",50,50,48,12),
        # OSCAR
        ("OSCAR","Yemek Masası",220,100,78,1),
        ("OSCAR","Konsol",220,50,80,2),
        ("OSCAR","TV Ünitesi",220,45,50,3),
        ("OSCAR","4'lü Koltuk (295 cm)",295,96,96,4),
        ("OSCAR","3,5'li Koltuk (255 cm)",255,96,96,5),
        ("OSCAR","3'lü Koltuk (235 cm)",235,96,96,6),
        ("OSCAR","Dinlenme Köşesi",295,166,70,7),
        ("OSCAR","Berjer",80,78,78,8),
        ("OSCAR","Tekli Koltuk",98,85,85,9),
        ("OSCAR","Şifonyer",136,47,90,10),
        ("OSCAR","Yan Sehpa",60,45,53,11),
        ("OSCAR","Orta Sehpa (Büyük)",100,75,30,12),
        ("OSCAR","Orta Sehpa (Küçük)",75,50,36,13),
        ("OSCAR","Zigon Sehpa (Büyük)",50,50,61,14),
        ("OSCAR","Zigon Sehpa (Küçük)",45,45,54,15),
        # PORTO
        ("PORTO","Yemek Masası",220,100,79,1),
        ("PORTO","Konsol",220,30,99,2),
        ("PORTO","TV Ünitesi",220,50,63,3),
        ("PORTO","3'lü Koltuk (242 cm)",242,90,90,4),
        ("PORTO","Tekli Koltuk",80,80,80,5),
        ("PORTO","Berjer",87,75,78,6),
        ("PORTO","Ayna",142,10,93,7),
        ("PORTO","Orta Sehpa (Büyük)",105,45,43,8),
        ("PORTO","Orta Sehpa (Küçük)",76,45,36,9),
        ("PORTO","Zigon Sehpa (Büyük)",46,46,60,10),
        ("PORTO","Zigon Sehpa (Küçük)",41,41,56,11),
    ]
    inserted = 0
    for coll,name,w,d,h,order in pieces:
        cid = cmap[coll]
        if (cid, name) in existing:
            # Sadece ölçü/sıra güncelle, duplicate yaratma
            conn.execute("""
                UPDATE pieces SET width_cm=?,depth_cm=?,height_cm=?,loading_order=?
                WHERE collection_id=? AND name=?
            """, (w,d,h,order,cid,name))
        else:
            conn.execute("""
                INSERT INTO pieces
                (collection_id,name,width_cm,depth_cm,height_cm,loading_order)
                VALUES(?,?,?,?,?,?)
            """, (cid,name,w,d,h,order))
            existing.add((cid,name))
            inserted += 1

    # Init piece_stock for all pieces
    conn.execute("""
        INSERT OR IGNORE INTO piece_stock (piece_id, status)
        SELECT id, 'available' FROM pieces
    """)

    # SLA defaults per collection (based on piece count)
    for coll_id, coll_name in cmap.items():
        cnt = conn.execute(
            "SELECT COUNT(*) c FROM pieces WHERE collection_id=?", (coll_id,)
        ).fetchone()[0]
        sla = 60 if cnt <= 8 else 90 if cnt <= 12 else 120
        conn.execute(
            "INSERT OR IGNORE INTO sla_config (collection_id,sla_minutes) VALUES(?,?)",
            (coll_id, sla)
        )

    conn.commit()
    print(f"✅ {inserted} yeni parça eklendi. SLA yapılandırıldı.")

def main():
    print("="*55)
    print("  FurnitureFlow – Veritabanı Kurulumu")
    print("="*55)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    migrate(conn)
    insert_defaults(conn)
    insert_furniture(conn)
    conn.close()
    print("\n🎉 Kurulum tamamlandı!  →  streamlit run app.py")
    print("="*55)

if __name__ == "__main__":
    main()
