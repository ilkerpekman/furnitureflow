# furnitureflow

FurnitureFlow
Logistics Integrity & Loading Workflow System

FurnitureFlow, mobilya sevkiyat operasyonlarında insan hafızasına dayalı süreçleri dijitalleştirmek amacıyla geliştirilmiş bir lojistik karar destek sistemidir.

Bu proje, Luxe Life Mobilya’daki saha deneyiminden doğan gerçek bir operasyonel problemi çözmek için tasarlanmıştır.

Problem

Mobilya sevkiyat operasyonlarında tek bir koleksiyon onlarca farklı parçadan oluşabilir.

Örneğin:

Massimo Koleksiyonu

Sideboard

Mirror Block

TV Unit

Shelf Modules

Leg Sets

Bu parçaların sadece doğru şekilde toplanması yetmez.

Aynı zamanda:

doğru sırayla yüklenmeleri

palet dengesinin korunması

kırılgan parçaların korunması

gerekmektedir.

Fakat sahadaki operasyon tamamen şu iki şeye dayanıyordu:

• Kağıt sipariş formları
• Personelin hafızası

Yeni bir personelin bu bilgileri öğrenmesi yaklaşık 1 ay sürüyordu.

Bu durum şu problemlere yol açıyordu:

eksik parça sevkiyatları

yanlış yükleme sırası

ürün hasarları

operasyonel yavaşlık

Kısacası fabrikanın kurumsal hafızası çalışanların zihnindeydi.

Solution

FurnitureFlow bu kurumsal hafızayı dijital bir sisteme aktarmak için geliştirildi.

Sistem üç temel prensip üzerine kuruldu:

1. Knowledge Digitization

Mobilya koleksiyonlarına ait tüm parçalar ve teknik ölçüler veritabanında modellenir.

2. Sequential Loading Logic

Sistem, personelin parçaları doğru sırayla yüklemesini zorunlu kılar.

3. Integrity Check

Tüm parçalar doğrulanmadan sevkiyat tamamlanamaz.

Böylece:

1 aylık ezber süreci
→ saniyeler süren dijital doğrulamaya dönüşür.

Key Features
Integrity Check System

Sevkiyat tamamlanmadan önce tüm parçalar doğrulanır.

Eksik parça varsa sistem sevkiyatı durdurur.

Sequential Loading Workflow

Parçaların palet üzerine stratejik yükleme sırası dijital olarak yönetilir.

Bu sayede:

palet dengesi korunur

ürün hasar riski azalır

operasyon hızlanır

Technical Dimension Modeling

Her parça için teknik ölçüler sisteme kaydedilir.

Bu sayede sistem:

yükleme sırasını optimize eder

operasyonel hataları azaltır

Operational Memory Digitization

Sahada çalışan personelin yıllar içinde edindiği operasyonel bilgi sistematik hale getirilmiştir.

FurnitureFlow’un temel amacı:

insan hafızasını operasyonel bir yazılım sistemine dönüştürmektir.

Tech Stack

Python
Streamlit
SQLite
SQLAlchemy

System Workflow

Sipariş oluşturulur

↓

Sistem koleksiyona ait parçaları getirir

↓

Personel parçaları sırayla doğrular

↓

Integrity Check çalışır

↓

Tüm parçalar doğrulanırsa sevkiyat tamamlanır

Real World Impact

FurnitureFlow aşağıdaki operasyonel kazanımları hedefler:

sevkiyat hatalarının azaltılması

yeni personelin adaptasyon süresinin kısalması

operasyonel hızın artması

kağıt tabanlı süreçlerin dijitalleşmesi

Future Improvements

barcode / QR scanning integration

warehouse performance analytics

shipment time SLA tracking

packing volume optimization

Author

İlker Pekman
Management Information Systems Student

Focused on building systems that bridge real-world operations and digital solutions.
