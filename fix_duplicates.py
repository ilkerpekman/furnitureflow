"""
FurnitureFlow – Duplicate Temizleyici
Yinelenen parçaları siler ve benzersizlik kısıtı ekler.
Çalıştır: python fix_duplicates.py
"""
import sqlite3

DB = "furnitureflow.db"

def fix():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Kaç duplicate var?
    dups = conn.execute("""
        SELECT collection_id, name, COUNT(*) cnt
        FROM pieces
        GROUP BY collection_id, name
        HAVING cnt > 1
    """).fetchall()

    if not dups:
        print("✅ Duplicate parça yok, her şey temiz.")
        conn.close()
        return

    total_removed = 0
    for d in dups:
        # En küçük id'li olanı koru, gerisini sil
        keep_id = conn.execute(
            "SELECT MIN(id) FROM pieces WHERE collection_id=? AND name=?",
            (d["collection_id"], d["name"])
        ).fetchone()[0]

        result = conn.execute(
            "DELETE FROM pieces WHERE collection_id=? AND name=? AND id!=?",
            (d["collection_id"], d["name"], keep_id)
        )
        removed = result.rowcount
        total_removed += removed
        print(f"  🗑  '{d['name']}' — {removed} kopya silindi (id={keep_id} korundu)")

    conn.commit()

    # Artık orphan order_items varsa temizle
    orphans = conn.execute("""
        DELETE FROM order_items
        WHERE piece_id NOT IN (SELECT id FROM pieces)
    """).rowcount
    conn.commit()

    print(f"\n✅ Toplam {total_removed} yinelenen parça silindi.")
    if orphans > 0:
        print(f"✅ {orphans} geçersiz sipariş kalemi temizlendi.")

    conn.close()
    print("\nUygulamayı yeniden başlat: streamlit run app.py")

if __name__ == "__main__":
    fix()
