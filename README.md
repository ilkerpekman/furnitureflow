![FurnitureFlow](banner.png)

# FurnitureFlow
**Lojistik Sipariş ve Depo Yönetim Sistemi**

🔗 [Canlı Demo](https://furnitureflow.streamlit.app) &nbsp;|&nbsp; Geliştirici: [İlker Pekman](https://github.com/ilkerpekman)

---

## Problem

Luxe Life Mobilya lojistik departmanında gözlemlediğim süreç problemleri:

- Tüm sevkiyat süreçleri **kağıt formlar** ve **personel hafızasına** dayanıyordu
- Tek bir koleksiyon onlarca farklı parçadan oluşuyor; doğru **yükleme sırası** kritik önem taşıyor
- Yeni bir personelin tüm koleksiyonları ve yükleme sırasını öğrenmesi **yaklaşık 1 ay** sürüyordu
- Eksik parça sevkiyatları ve yanlış istifleme sık yaşanan operasyonel kayıplardı

Fabrikanın kurumsal hafızası çalışanların zihnindeydi.

---

## Çözüm

FurnitureFlow bu kurumsal hafızayı dijital bir sisteme aktarmak için geliştirildi.

> Luxe Life Mobilya lojistik departmanında tespit ettiğim manuel süreç problemlerini ortadan kaldırmak için sıralı tik atma mekanizması, bütünlük kontrolü, uzman tanımlı yükleme sırası, gerçek zamanlı SLA takibi ve rol tabanlı erişim kontrolünü birleştiren bir karar destek sistemi geliştirdim.

---

## Özellikler

| Özellik | Açıklama |
|---|---|
| ✅ **Bütünlük Kontrolü** | Tüm parçalar doğrulanmadan sevkiyat tamamlanamaz |
| 📋 **Uzman Tanımlı Yükleme Sırası** | Her koleksiyon için optimize edilmiş sıralama |
| ⏱ **Gerçek Zamanlı SLA Takibi** | Kritik siparişler için süre uyarı sistemi |
| 🔑 **Rol Tabanlı Erişim** | Admin / Yönetici / Personel yetki seviyeleri |
| 📄 **Otomatik Çeki Listesi** | PDF ve Excel formatında sevkiyat belgesi |
| 🔔 **Bildirim Sistemi** | Anlık operasyonel uyarılar |
| 📜 **Denetim Kaydı** | Tüm işlemlerin tam izlenebilir kaydı |
| 📊 **Analitik Dashboard** | Personel performansı ve SLA raporları |

---

## Teknoloji

```
Python · Streamlit · SQLite · ReportLab · Pandas · openpyxl
```

---

## Kurulum

```bash
git clone https://github.com/ilkerpekman/furnitureflow
cd furnitureflow
pip install -r requirements.txt
python init_db.py
python generate_sample_data.py
streamlit run app.py
```

## Demo Hesapları

| Rol | Kullanıcı | Şifre |
|---|---|---|
| 🔑 Admin | `admin` | `admin123` |
| 📋 Yönetici | `yonetici` | `yonetici123` |
| 👷 Personel | `personel` | `personel123` |

---

## Sistem İş Akışı

```
Sipariş Oluşturulur
        ↓
Sistem koleksiyona ait parçaları getirir
        ↓
Personel parçaları sırayla tik atarak doğrular
        ↓
Bütünlük Kontrolü (Integrity Check) çalışır
        ↓
Tüm parçalar onaylanırsa → Çeki Listesi üretilir
        ↓
Sevkiyat tamamlanır
```

---

*Luxe Life Mobilya lojistik departmanında gözlemlenen gerçek operasyonel problemlerden doğdu.*

