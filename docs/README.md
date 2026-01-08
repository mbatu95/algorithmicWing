# Algorithmic Wing - Parametrik Kanat Tasarımı

3D parametrik kanat tasarımı ve görselleştirme aracı. Three.js kullanarak gerçek zamanlı kanat geometrisi ve aerodinamik hesaplamaları sunar.

## 🚀 Demo

[Demo'yu GitHub Pages üzerinden görüntüle](https://mbatu95.github.io/algorithmicWing/)

## ✨ Özellikler

- **Parametrik Tasarım**: Kanat açıklığı, veter uzunluğu, NACA profili ve daha fazlası
- **Gerçek Zamanlı Görselleştirme**: Three.js ile 3D kanat modeli
- **Aerodinamik Hesaplamalar**: Kaldırma katsayısı, sürükleme ve performans metrikleri
- **İnteraktif Kontroller**: Slider'lar ile canlı parametre ayarlama
- **GitHub Pages Uyumlu**: Backend olmadan çalışan demo modu

## 🎮 Parametreler

- **Kanat Açıklığı**: 6-20 metre arası ayarlanabilir
- **Kök Veter**: Kanadın kök kısmındaki veter uzunluğu
- **NACA Profili**: 4 haneli NACA kanat profili (örn: 4656)
- **Dihedral Açısı**: -20° ile +20° arası kanat açısı
- **Daraltma Oranı**: Uç veter / Kök veter oranı
- **Kayma Miktarı**: Kanat kamber ayarı

## 🛠️ Yerel Kurulum

### Gereksinimler

- Python 3.8+
- Modern web tarayıcı

### Backend ile Çalıştırma

```bash
# Backend'i başlat
cd backend
python main.py

# Frontend'i aç
cd ../frontend
# index.html dosyasını tarayıcıda aç
```

### Sadece Frontend (GitHub Pages Modu)

```bash
cd docs
# index.html dosyasını tarayıcıda aç
# veya bir local server kullan:
python -m http.server 8080
```

## 📁 Proje Yapısı

```
algorithmicWing/
├── backend/          # FastAPI backend
│   ├── main.py      # Ana API
│   └── plane/       # Kanat geometri modülleri
├── frontend/        # Orijinal frontend (backend gerektirir)
├── docs/            # GitHub Pages versiyonu (standalone)
│   ├── index.html
│   └── wing_api_client.js
└── README.md
```

## 🌐 GitHub Pages Deploy

1. Repository ayarlarına git
2. **Settings** > **Pages** sekmesine tıkla
3. **Source** olarak `Deploy from a branch` seç
4. **Branch** olarak `main` (veya mevcut branch) ve `/docs` klasörünü seç
5. **Save** butonuna tıkla
6. Birkaç dakika içinde site hazır olacak

## 🔧 Teknolojiler

- **Frontend**: Three.js, JavaScript ES6+
- **Backend**: Python, FastAPI, NumPy
- **3D Rendering**: WebGL via Three.js
- **Deployment**: GitHub Pages

## 📊 Aerodinamik Hesaplamalar

Uygulama şu metrikleri hesaplar:

- **C_L** (Kaldırma Katsayısı): Temel ve efektif değerler
- **C_Di** (İndüklenmiş Sürükleme): Kanat verimliliği
- **Dihedral Etkisi**: Yan denge üzerine etki
- **Kaldırma Kuvveti**: Örnek hız ve hücum açısı için

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👤 Yazar

Murat Batuhan Günaydın

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır. Büyük değişiklikler için lütfen önce bir issue açarak ne değiştirmek istediğinizi tartışın.
