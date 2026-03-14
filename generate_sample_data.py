"""
FurnitureFlow v2.0 – Örnek Veri Üretici
Anlamlı ürün gruplarına göre rastgele siparişler oluşturur.
Çalıştırmak için: python generate_sample_data.py
"""

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta

DB = "furnitureflow.db"

# ── Türkçe müşteri isimleri ────────────────────────────────────────────────────
CUSTOMERS = [
    ("Ahmet Yılmaz",     "ahmet.yilmaz@gmail.com"),
    ("Fatma Kaya",       "fatma.kaya@hotmail.com"),
    ("Mehmet Demir",     "mehmet.demir@outlook.com"),
    ("Ayşe Çelik",       "ayse.celik@gmail.com"),
    ("Mustafa Şahin",    "mustafa.sahin@gmail.com"),
    ("Zeynep Arslan",    "zeynep.arslan@hotmail.com"),
    ("İbrahim Kurt",     "ibrahim.kurt@gmail.com"),
    ("Hatice Özdemir",   "hatice.ozdemir@gmail.com"),
    ("Ali Aydın",        "ali.aydin@outlook.com"),
    ("Emine Yıldırım",   "emine.yildirim@gmail.com"),
    ("Hüseyin Doğan",    "huseyin.dogan@hotmail.com"),
    ("Merve Kılıç",      "merve.kilic@gmail.com"),
    ("Ömer Aslan",       "omer.aslan@gmail.com"),
    ("Elif Yıldız",      "elif.yildiz@outlook.com"),
    ("Yusuf Çetin",      "yusuf.cetin@gmail.com"),
    ("Selin Koç",        "selin.koc@hotmail.com"),
    ("Burak Avcı",       "burak.avci@gmail.com"),
    ("Nur Güneş",        "nur.gunes@gmail.com"),
    ("Serkan Polat",     "serkan.polat@outlook.com"),
    ("Canan Aktaş",      "canan.aktas@gmail.com"),
    ("Kemal Bozkurt",    "kemal.bozkurt@hotmail.com"),
    ("Gül Toprak",       "gul.toprak@gmail.com"),
    ("Tarık Uzun",       "tarik.uzun@gmail.com"),
    ("Leyla Karahan",    "leyla.karahan@outlook.com"),
    ("Berke Güngör",      "berke.gungor@gmail.com"),
]

# ── Anlamlı ürün grubu kategorileri ──────────────────────────────────────────
# Her parça adında geçen anahtar kelimeler → grup adı
# Bir parça birden fazla gruba girebilir; gruplar oluşturulurken bütünlük korunur

PIECE_GROUPS = {
    "koltuk_grubu": [
        "koltuk", "berjer", "tekli koltuk", "dinlenme köşesi", "angel berjer",
    ],
    "yemek_odasi_grubu": [
        "yemek masası", "sandalye", "puf sedir",
    ],
    "depolama_grubu": [
        "konsol", "şifonyer", "tv ünitesi",
    ],
    "orta_sehpa_grubu": [
        "orta sehpa", "zigon sehpa", "yan sehpa",
    ],
    "aksesuar_grubu": [
        "ayna",
    ],
}

# Grup adı → Türkçe etiket
GROUP_LABELS = {
    "koltuk_grubu":     "Koltuk Grubu",
    "yemek_odasi_grubu":"Yemek Odası Grubu",
    "depolama_grubu":   "Depolama Grubu",
    "orta_sehpa_grubu": "Orta Sehpa Grubu",
    "aksesuar_grubu":   "Aksesuar Grubu",
}

# Her grubu sipariş içinde dahil etme olasılığı
GROUP_PROBABILITIES = {
    "koltuk_grubu":      0.75,
    "yemek_odasi_grubu": 0.60,
    "depolama_grubu":    0.55,
    "orta_sehpa_grubu":  0.65,
    "aksesuar_grubu":    0.30,
}


def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def classify_piece(piece_name: str) -> list:
    """Parça adına göre hangi gruplara girdiğini döndürür."""
    name_lower = piece_name.lower().replace("i̇","i").replace("ı","i").replace("ş","s").replace("ğ","g").replace("ü","u").replace("ö","o").replace("ç","c")
    groups = []
    for group, keywords in PIECE_GROUPS.items():
        for kw in keywords:
            kw_norm = kw.lower().replace("i̇","i").replace("ı","i").replace("ş","s").replace("ğ","g").replace("ü","u").replace("ö","o").replace("ç","c")
            if kw_norm in name_lower:
                groups.append(group)
                break
    return groups if groups else ["diger"]


def build_collection_groups(conn, collection_id: int) -> dict:
    """
    Bir koleksiyonun parçalarını anlamlı gruplara ayırır.
    Döner: {grup_adi: [piece_id, ...]}
    """
    pieces = conn.execute(
        "SELECT id, name FROM pieces WHERE collection_id=? ORDER BY loading_order",
        (collection_id,)
    ).fetchall()

    groups: dict[str, list] = {}
    for p in pieces:
        piece_groups = classify_piece(p["name"])
        for g in piece_groups:
            groups.setdefault(g, [])
            if p["id"] not in groups[g]:
                groups[g].append(p["id"])

    return groups


def select_pieces_for_order(conn, collection_id: int) -> list:
    """
    Bir sipariş için anlamlı parça seçimi yapar.
    En az 1 grup seçilir; her grubun tüm parçaları dahil edilir.
    Döner: [piece_id, ...]
    """
    groups = build_collection_groups(conn, collection_id)

    if not groups:
        return []

    selected_ids = set()

    # Olasılığa göre grupları seç
    for group_name, piece_ids in groups.items():
        prob = GROUP_PROBABILITIES.get(group_name, 0.5)
        if random.random() < prob:
            selected_ids.update(piece_ids)

    # En az 1 grup seçili olsun
    if not selected_ids:
        fallback_group = random.choice(list(groups.keys()))
        selected_ids.update(groups[fallback_group])

    # Yükleme sırasına göre sırala
    if selected_ids:
        rows = conn.execute(
            f"SELECT id FROM pieces WHERE id IN ({','.join('?'*len(selected_ids))}) "
            f"ORDER BY loading_order",
            list(selected_ids)
        ).fetchall()
        return [r["id"] for r in rows]

    return []


def random_past_date(days_back: int = 60) -> str:
    """Son N gün içinde rastgele bir tarih üretir."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(7, 19),
        minutes=random.randint(0, 59)
    )
    dt = datetime.now() - delta
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def generate_order_number(index: int) -> str:
    return f"ORD-2026-{index:03d}"


def generate_orders(n: int = 25, completed_ratio: float = 0.65) -> dict:
    """
    n adet sipariş oluşturur.
    completed_ratio: tamamlanmış siparişlerin oranı
    """
    conn = get_conn()

    # Mevcut siparişlerdeki en yüksek sıra numarasını bul
    last = conn.execute(
        "SELECT order_number FROM orders ORDER BY id DESC LIMIT 1"
    ).fetchone()

    start_idx = 1
    if last:
        try:
            start_idx = int(last["order_number"].split("-")[-1]) + 1
        except Exception:
            start_idx = 100

    collections = conn.execute(
        "SELECT id, name FROM collections"
    ).fetchall()

    # Creators: admin/yonetici
    creators = conn.execute(
        "SELECT username FROM users WHERE role IN ('admin','yonetici') AND is_active=1"
    ).fetchall()
    creator_names = [u["username"] for u in creators] or ["admin"]

    # Personnel who actually do the work
    personels = conn.execute(
        "SELECT username FROM users WHERE role='personel' AND is_active=1"
    ).fetchall()
    personel_names = [u["username"] for u in personels] or ["personel"]

    PRIORITIES = ["normal","normal","normal","high","high","urgent","low"]

    created_count   = 0
    skipped_count   = 0
    group_stats: dict[str, int] = {}

    for i in range(n):
        order_number = generate_order_number(start_idx + i)

        existing = conn.execute(
            "SELECT id FROM orders WHERE order_number=?", (order_number,)
        ).fetchone()
        if existing:
            skipped_count += 1
            continue

        collection   = random.choice(collections)
        customer     = random.choice(CUSTOMERS)
        creator      = random.choice(creator_names)
        assigned     = random.choice(personel_names)
        priority     = random.choice(PRIORITIES)
        created_dt   = random_past_date(60)

        # SLA: 60–120 dk arası
        sla_minutes = random.choice([60, 75, 90, 90, 90, 105, 120])

        # started_at: 5–30 dakika sonra created_at'tan
        c_dt = datetime.strptime(created_dt, "%Y-%m-%d %H:%M:%S")
        start_delay = random.randint(5, 30)
        started_dt  = (c_dt + timedelta(minutes=start_delay)).strftime("%Y-%m-%d %H:%M:%S")

        is_completed = random.random() < completed_ratio
        if is_completed:
            # Bazıları SLA içinde, bazıları aşmış
            sla_ok = random.random() < 0.72   # %72 SLA içinde biter
            if sla_ok:
                minutes_later = random.randint(int(sla_minutes*0.3), int(sla_minutes*0.95))
            else:
                minutes_later = random.randint(int(sla_minutes*1.05), int(sla_minutes*2.0))
            completed_dt = (c_dt + timedelta(minutes=start_delay+minutes_later)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            status = "completed"
        else:
            completed_dt = None
            status = "pending"

        piece_ids = select_pieces_for_order(conn, collection["id"])
        if not piece_ids:
            skipped_count += 1
            continue

        cursor = conn.execute("""
            INSERT INTO orders
            (order_number, collection_id, status, customer_name,
             customer_email, created_by, assigned_to, priority,
             sla_minutes, created_at, started_at, completed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            order_number, collection["id"], status,
            customer[0], customer[1], creator, assigned, priority,
            sla_minutes, created_dt, started_dt, completed_dt
        ))
        order_id = cursor.lastrowid

        # Parçaları ekle
        for pid in piece_ids:
            # Tamamlanmışlarda tik atılmış + bazıları hasarlı
            is_checked = 1 if is_completed else 0
            item_status = "normal"
            item_note   = ""

            if is_completed and random.random() < 0.12:
                item_status = random.choice(["damaged", "missing"])
                if item_status == "damaged":
                    item_note = random.choice([
                        "Nakliye sırasında çizilme",
                        "Köşe bölümünde çatlak",
                        "Kumaşta leke",
                        "Boya dökülmesi",
                        "Küçük çarpma hasarı",
                        "Vidalarda gevşeme",
                        "Yüzey çizikleri",
                    ])
                else:
                    item_note = random.choice([
                        "Depoda bulunamadı",
                        "Temin edilecek",
                        "Üretimde gecikme",
                        "Sevkiyat listesinde yok",
                        "Stok kontrolü bekleniyor",
                    ])

            checked_at = completed_dt if is_checked else None
            conn.execute("""
                INSERT INTO order_items
                (order_id, piece_id, is_checked, item_status, item_note, checked_at)
                VALUES (?,?,?,?,?,?)
            """, (order_id, pid, is_checked, item_status, item_note, checked_at))

        # Grup istatistiği
        groups_used = build_collection_groups(conn, collection["id"])
        for g, ids in groups_used.items():
            if any(pid in piece_ids for pid in ids):
                group_stats[g] = group_stats.get(g, 0) + 1

        created_count += 1

    conn.commit()
    conn.close()

    return {
        "created": created_count,
        "skipped": skipped_count,
        "group_stats": group_stats,
    }


# ── Bildirim üretici ──────────────────────────────────────────────────────────
def generate_notifications(n: int = 12):
    conn = get_conn()

    # Mevcut bildirimleri kontrol et
    existing = conn.execute("SELECT COUNT(*) c FROM notifications").fetchone()["c"]
    if existing >= n:
        conn.close()
        return 0

    orders = conn.execute(
        "SELECT id, order_number FROM orders ORDER BY RANDOM() LIMIT 20"
    ).fetchall()
    if not orders:
        conn.close()
        return 0

    NOTIF_TEMPLATES = [
        ("new_order",  "Yeni sipariş oluşturuldu: #{num} ({extra})"),
        ("completed",  "Sipariş tamamlandı: #{num} — Hazırlık süresi {extra} dk"),
        ("damage",     "Hasar bildirimi: #{num} — {extra}"),
        ("stock",      "Stok uyarısı: {extra} — Tedarikçide"),
        ("sla",        "SLA aşımı: #{num} — {extra} dk gecikme"),
        ("new_order",  "Acil sipariş alındı: #{num}"),
        ("completed",  "Sipariş #{num} SLA içinde tamamlandı"),
        ("damage",     "#{num}: Köşe bölümünde hasar tespit edildi"),
        ("stock",      "Stok güncellendi: {extra} depoya geldi"),
        ("sla",        "Dikkat: #{num} siparişi SLA sınırına yaklaşıyor"),
        ("new_order",  "#{num} siparişi personele atandı"),
        ("completed",  "Günlük hedef aşıldı — {extra} sipariş tamamlandı"),
    ]

    DAMAGE_DETAILS = [
        "TV Ünitesi — Boya dökülmesi",
        "Konsol — Köşe çatlağı",
        "3'lü Koltuk — Kumaş lekesi",
        "Orta Sehpa — Cam çizilme",
        "Yemek Masası — Ayak hasarı",
        "Berjer — Kumaş yırtığı",
        "Şifonyer — Kapak menteşe hasarı",
        "Zigon Sehpa — Üst yüzey çizilme",
    ]
    STOCK_DETAILS = ["Konsol", "TV Ünitesi", "Berjer", "Orta Sehpa", "Zigon Sehpa"]

    added = 0
    to_add = n - existing
    for i in range(to_add):
        tpl_type, tpl_msg = random.choice(NOTIF_TEMPLATES)
        order = random.choice(orders)
        num   = order["order_number"]

        if "{extra}" in tpl_msg:
            if tpl_type == "damage":  extra = random.choice(DAMAGE_DETAILS)
            elif tpl_type == "stock": extra = random.choice(STOCK_DETAILS)
            elif tpl_type == "sla":   extra = str(random.randint(10, 45))
            elif tpl_type == "completed": extra = str(random.randint(35, 95))
            else: extra = random.choice(["HILTON", "MASSIMO", "OSCAR"])
            msg = tpl_msg.format(num=num, extra=extra)
        else:
            msg = tpl_msg.format(num=num)

        is_read = 1 if random.random() < 0.6 else 0
        dt = (datetime.now() - timedelta(
            hours=random.randint(0, 72),
            minutes=random.randint(0, 59)
        )).strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO notifications (type, message, order_id, is_read, created_at)
            VALUES (?,?,?,?,?)
        """, (tpl_type, msg, order["id"], is_read, dt))
        added += 1

    conn.commit()
    conn.close()
    return added


# ── Denetim kaydı üretici ─────────────────────────────────────────────────────
def generate_audit_logs(n: int = 15):
    conn = get_conn()

    existing = conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]
    if existing >= n:
        conn.close()
        return 0

    orders = conn.execute(
        "SELECT id, order_number, collection_id FROM orders ORDER BY RANDOM() LIMIT 30"
    ).fetchall()
    users_a = conn.execute(
        "SELECT username FROM users WHERE is_active=1"
    ).fetchall()
    usernames = [u["username"] for u in users_a] or ["admin"]

    if not orders:
        conn.close()
        return 0

    AUDIT_TEMPLATES = [
        ("CREATE",          "order",       lambda o: f"#{o['order_number']} oluşturuldu"),
        ("START",           "order",       lambda o: f"#{o['order_number']} hazırlamaya başlandı"),
        ("COMPLETE",        "order",       lambda o: f"#{o['order_number']} tamamlandı"),
        ("DAMAGE",          "order_item",  lambda o: f"#{o['order_number']}: Konsol — Hasarlı"),
        ("DAMAGE",          "order_item",  lambda o: f"#{o['order_number']}: TV Ünitesi — Eksik"),
        ("ADD_DELIVERY",    "deliveries",  lambda o: f"#{o['order_number']} → Osmangazi, Bursa"),
        ("ADD_DELIVERY",    "deliveries",  lambda o: f"#{o['order_number']} → Nilüfer, Bursa"),
        ("UPDATE_DELIVERY", "deliveries",  lambda o: f"#{o['order_number']} → 🚚 Yolda"),
        ("UPDATE_DELIVERY", "deliveries",  lambda o: f"#{o['order_number']} → ✅ Teslim Edildi"),
        ("ROUTE_PLAN",      "route_plans", lambda o: f"2026-03-{random.randint(10,14):02d} | TIR | {random.randint(3,8)} durak | {random.randint(25,120)} km"),
        ("CREATE",          "order",       lambda o: f"#{o['order_number']} ACİL öncelikle oluşturuldu"),
        ("COMPLETE",        "order",       lambda o: f"#{o['order_number']} SLA içinde tamamlandı — {random.randint(35,85)} dk"),
        ("DELETE",          "order",       lambda o: f"Test siparişi silindi"),
        ("LOGIN",           "users",       lambda o: "Sisteme giriş yapıldı"),
        ("START",           "order",       lambda o: f"#{o['order_number']} personele atandı ve başlatıldı"),
    ]

    added = 0
    to_add = n - existing
    for i in range(to_add):
        action, entity, detail_fn = random.choice(AUDIT_TEMPLATES)
        order    = random.choice(orders)
        username = random.choice(usernames)
        detail   = detail_fn(order)
        dt       = (datetime.now() - timedelta(
            hours=random.randint(0, 168),
            minutes=random.randint(0, 59)
        )).strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO audit_log (username, action, entity, entity_id, detail, created_at)
            VALUES (?,?,?,?,?,?)
        """, (username, action, entity, str(order["id"]), detail, dt))
        added += 1

    conn.commit()
    conn.close()
    return added


# ── Teslimat & Rota üretici ───────────────────────────────────────────────────
BURSA_DISTRICTS = {
    "Osmangazi":   (40.1826, 29.0665),
    "Nilüfer":     (40.2131, 28.9769),
    "Yıldırım":    (40.1908, 29.1147),
    "Gemlik":      (40.4319, 29.1536),
    "Mudanya":     (40.3747, 28.8839),
    "İnegöl":      (40.0785, 29.5124),
    "Gürsu":       (40.2167, 29.1833),
    "Kestel":      (40.1833, 29.2167),
}

STREET_NAMES = [
    "Atatürk Cad.", "Cumhuriyet Sok.", "İstiklal Cad.", "Barış Mah.",
    "Fatih Sok.", "Yıldız Cad.", "Çiçek Sok.", "Lale Mah.",
    "Gül Sok.", "Mimar Sinan Cad.", "Zafer Cad.", "Hürriyet Sok.",
]

TIME_WINDOWS = ["09:00-12:00", "12:00-15:00", "15:00-18:00", "09:00-18:00"]
DEL_STATUSES = ["pending", "pending", "in_transit", "delivered", "delivered"]


def generate_deliveries(n: int = 10):
    conn = get_conn()

    existing = conn.execute("SELECT COUNT(*) c FROM deliveries").fetchone()["c"]
    if existing >= n:
        conn.close()
        return 0

    # Tamamlanmış ve teslimatı olmayan siparişler
    orders = conn.execute("""
        SELECT o.id, o.order_number FROM orders o
        WHERE o.status='completed'
          AND o.id NOT IN (SELECT order_id FROM deliveries)
        ORDER BY RANDOM() LIMIT ?
    """, (n - existing,)).fetchall()

    if not orders:
        conn.close()
        return 0

    added = 0
    districts = list(BURSA_DISTRICTS.keys())

    # Spread over last 14 days
    base_date = datetime.now().date()

    for i, o in enumerate(orders):
        district = random.choice(districts)
        lat, lng  = BURSA_DISTRICTS[district]
        # Add small random offset so addresses aren't identical
        lat += random.uniform(-0.015, 0.015)
        lng += random.uniform(-0.015, 0.015)

        street  = random.choice(STREET_NAMES)
        no      = random.randint(1, 120)
        address = f"{street} No:{no}"

        # Dates: mix of past, today, future
        day_offset = random.randint(-7, 5)
        del_date   = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        time_win   = random.choice(TIME_WINDOWS)

        # Past deliveries are likely delivered, future ones pending
        if day_offset < -1:
            status = random.choice(["delivered", "delivered", "in_transit"])
        elif day_offset == 0:
            status = random.choice(["in_transit", "pending", "delivered"])
        else:
            status = "pending"

        conn.execute("""
            INSERT INTO deliveries
            (order_id, address, district, city, lat, lng, delivery_date, time_window, status)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (o["id"], address, district, "Bursa", round(lat, 4), round(lng, 4),
              del_date, time_win, status))
        added += 1

    conn.commit()

    # Generate a few route plans for days that have multiple deliveries
    route_count = conn.execute("SELECT COUNT(*) c FROM route_plans").fetchone()["c"]
    if route_count < 5:
        vehicles = ["TIR", "Büyük Kamyon", "Orta Kamyon"]
        usernames2 = [u["username"] for u in conn.execute(
            "SELECT username FROM users WHERE role IN ('admin','yonetici') AND is_active=1"
        ).fetchall()] or ["admin"]

        for day_offset in [-5, -3, -1, 0, 2]:
            plan_date = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            # Get deliveries for that day
            day_dels = conn.execute(
                "SELECT order_id FROM deliveries WHERE delivery_date=?", (plan_date,)
            ).fetchall()
            if not day_dels:
                continue
            stop_ids  = [str(d["order_id"]) for d in day_dels]
            total_km  = round(random.uniform(18, 95), 1)
            vehicle   = random.choice(vehicles)
            creator   = random.choice(usernames2)
            created_dt = (datetime.now() - timedelta(
                days=abs(day_offset)+1,
                hours=random.randint(7, 17)
            )).strftime("%Y-%m-%d %H:%M:%S")

            conn.execute("""
                INSERT OR IGNORE INTO route_plans
                (plan_date, vehicle_name, stop_order, total_km_est, created_by, created_at)
                VALUES (?,?,?,?,?,?)
            """, (plan_date, vehicle, ",".join(stop_ids), total_km, creator, created_dt))

    conn.commit()
    conn.close()
    return added


def generate_all_extras(notif_n=12, audit_n=15, delivery_n=10):
    n1 = generate_notifications(notif_n)
    n2 = generate_audit_logs(audit_n)
    n3 = generate_deliveries(delivery_n)
    return {"notifications": n1, "audit_logs": n2, "deliveries": n3}


def print_summary(result: dict):
    print("\n" + "=" * 55)
    print("  Örnek Veri Üretimi Tamamlandı")
    print("=" * 55)
    print(f"  ✅ Oluşturulan sipariş : {result['created']}")
    print(f"  ⏭  Atlanan (zaten var) : {result['skipped']}")
    print("\n  Ürün grubu dağılımı:")
    for g, cnt in sorted(result["group_stats"].items(),
                         key=lambda x: -x[1]):
        label = GROUP_LABELS.get(g, g)
        bar   = "█" * min(cnt, 30)
        print(f"    {label:<25} {bar} ({cnt})")
    print("=" * 55)


if __name__ == "__main__":
    import sys

    n = 25
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass

    print(f"⏳ {n} örnek sipariş oluşturuluyor...")
    result = generate_orders(n=n)
    print_summary(result)

    print("\n⏳ Ek veriler oluşturuluyor (bildirim, denetim, teslimat)...")
    extras = generate_all_extras(notif_n=12, audit_n=15, delivery_n=10)
    print(f"  📬 Bildirim eklendi     : {extras['notifications']}")
    print(f"  📜 Denetim kaydı eklendi: {extras['audit_logs']}")
    print(f"  📍 Teslimat eklendi     : {extras['deliveries']}")
    print("\nUygulamayı başlatmak için: streamlit run app.py")
