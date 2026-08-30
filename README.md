# 🌿 GyepMester – Okos Gyepápolási Webalkalmazás és Rendszerdokumentáció

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![GitHub repo](https://img.shields.io/badge/GitHub-JosephWolf1986%2FGyepMester-181717?style=flat&logo=github&logoColor=white)](https://github.com/JosephWolf1986/GyepMester)

A **GyepMester** egy személyre szabott, modern, intelligens gyepápolási és kertgondozási webalkalmazás. Segítségével a kerttulajdonosok professzionális szinten követhetik nyomon gyepeik állapotát, naplózhatják az elvégzett tevékenységeket (öntözés, fűnyírás, trágyázás, gyepszellőztetés, gyomkezelés, növényvédelem), és a valós helyi időjáráshoz, évszakhoz és talajadottságokhoz igazított okos javaslatokat kapnak a tökéletes pázsit eléréséhez.

---

## 📌 Főbb Funkciók

- 📊 **Átfogó Műszerfal (Dashboard)**: Gyorsstatisztikák a területekről, utolsó ápolási dátumok, valós idejű helyi időjárás-előrejelzés és azonnali, sürgősség szerint rangsorolt teendők.
- 🌱 **Részletes Gyep Profilok**:
  - Alapadatok: név, terület (m²), helyszín (város), talajösszetétel, napfény-kitettség, fénykép.
  - **Művelési mód**: Extenzív, Normál, Intenzív.
  - **Nyírási technológia**: Kézi vagy Gépi fűnyírás.
  - **Karbantartás-követés**: Fűnyírókés utolsó élezési dátumának rögzítése.
  - **Kezdő tápanyag-előzmény**: Új gyep felvételekor közvetlenül megadható az utolsó trágyázás időpontja és terméke.
- 📦 **Beépített Termékkatalógus & Dinamikus Bővíthetőség**:
  - Előre feltöltött fűmagok (*Barenbrug, DLF Turfline, Eurogreen, Scotts*).
  - Előre feltöltött műtrágyák (*ICL Landscaper Pro – köztük a Stress Control 16-5-22, All Round, Full Season, Compo, Genezis, T.Garden*).
  - **Azonnali AJAX termékmentés**: Új műtrágyák az űrlap elhagyása nélkül rögzíthetők a rendszerbe NPK kalkulátorral.
- 📋 **Tevékenységnaplózás (6 modul)**:
  - 💧 **Öntözés**: időtartam (perc), kijuttatott vízmennyiség (l/m²), öntözési módszer.
  - ✂️ **Fűnyírás**: vágási magasság (cm), gyep állapota vágás előtt.
  - 🌱 **Trágyázás**: termékválasztó vagy egyedi N-P-K arányok megadása, kiszórt mennyiség (g/m²).
  - 🌬️ **Gyepszellőztetés**: szellőztetési módszer, felülvetés rögzítése.
  - 🌿 **Gyomirtás**: mechanikus / kézi / vegyszeres kezelés, fertőzöttségi szint, felhasznált termék.
  - 🐛 **Kártevő- és Betegségvédelem**: gombásodás, rovarok, vakondtúrás, súlyosság, kezelési mód.
- 🧠 **Okos Javaslatgeneráló Motor**:
  - Számításba veszi a talajtípust, az évszakot, a csapadékot és az utolsó beavatkozás óta eltelt időt.
  - Sürgősségi szintek (`high`, `medium`, `low`) pontos liter- és gramm-kalkulációkkal.
- 📅 **Interaktív Havi Naptár**: Havi bontású, színkódolt naptár és idővonal az elvégzett munkák áttekintésére.
- 🖼️ **Optimalizált Médiafeldolgozás**: Feltöltött képek automatikus átméretezése, EXIF tájolási hiba javítása és WebP formátumba tömörítése.
- 🌙 **Modern Sötét Téma (Dark UI)**: Organikus smaragd és természet-zöld hangsúlyok, letisztult tipográfia, finom mikró-animációk és teljes reszponzivitás mobilon és asztali gépen.

---

## 1. 🏗️ Rendszerarchitektúra és Mappastruktúra

Az alkalmazás az **MVC (Model-View-Controller)** mintát követi:

```
GyepMester/
│
├── app.py                     # Alkalmazás belépési pont, URL útvonalak, kontrollerek
├── config.py                  # Konfigurációs beállítások (DB, Upload, OpenWeather)
├── models.py                  # SQLAlchemy adatmodellek és relációk
├── seed_data.py               # Fűmag- és műtrágya-katalógus inicializáló & frissítő
├── requirements.txt           # Python csomagfüggőségek
├── README.md                  # Projekt- és rendszerdokumentáció
├── .env.example               # Példa környezeti változók fájlja
├── .gitignore                 # Git verziókövetésből kizárt fájlok
│
├── utils/                     # Üzleti logika és segédmodulok
│   ├── helpers.py             # Képfeldolgozás (Pillow, WebP, EXIF), dátum kalkulációk
│   ├── suggestions.py         # Intelligens szabálymotor (ápolási javaslatok)
│   └── weather.py             # OpenWeatherMap API integráció (aktuális időjárás & előrejelzés)
│
├── static/                    # Statikus webes erőforrások
│   ├── css/
│   │   └── style.css          # Prémium sötét CSS design rendszer és tokenek
│   ├── js/
│   │   └── main.js            # Frontend interakciók, AJAX termék-kitöltő, naptár motor
│   └── uploads/               # Feltöltött, optimalizált felhasználói fotók (.gitkeep-pel)
│
└── templates/                 # Jinja2 HTML sablonok
    ├── base.html              # Fő alkalmazás layout (navigáció, értesítések)
    ├── dashboard.html         # Főoldali összefoglaló műszerfal
    ├── suggestions.html       # Priorizált javaslatok gyepenként
    ├── calendar.html          # Interaktív havi ápolási naptár
    ├── auth/                  # Hitelesítés
    │   ├── login.html         # Bejelentkezés
    │   └── register.html      # Regisztráció
    ├── profile/               # Gyep Profil CRUD
    │   ├── list.html          # Profilok listája
    │   ├── new.html           # Új gyep felvétele (művelés, nyírás, tápanyag-előzmények)
    │   ├── detail.html        # Részletes adatlap és gyorsműveletek
    │   └── edit.html          # Profil szerkesztése
    ├── activities/            # Tevékenységnapló
    │   ├── list.html          # Szűrhető naplóbejegyzések listája
    │   └── add.html           # Új tevékenység rögzítése
    └── errors/                # Egyedi hibaoldalak
        ├── 403.html           # Hozzáférés megtagadva
        └── 404.html           # Nem található oldal
```

---

## 2. 🗄️ Adatmodell és Adatbázis-séma

A rendszer adatbázis-kezelését a **Flask-SQLAlchemy** ORM látja el. Támogatja a helyi **SQLite** fájlalapú adatbázist és a felhőalapú **PostgreSQL** (pl. Supabase) rendszert is.

```mermaid
erDiagram
    User ||--o{ LawnProfile : "birtokol (1:N)"
    GrassSeedProduct ||--o{ LawnProfile : "fűmag típus (1:N)"
    FertilizerProduct ||--o{ FertilizingLog : "műtrágya típus (1:N)"
    
    LawnProfile ||--o{ WateringLog : "öntözések (1:N)"
    LawnProfile ||--o{ MowingLog : "fűnyírások (1:N)"
    LawnProfile ||--o{ FertilizingLog : "trágyázások (1:N)"
    LawnProfile ||--o{ AerationLog : "szellőztetések (1:N)"
    LawnProfile ||--o{ WeedLog : "gyomkezelések (1:N)"
    LawnProfile ||--o{ PestLog : "kártevő megfigyelések (1:N)"

    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        datetime created_at
    }

    LawnProfile {
        int id PK
        int user_id FK
        string name
        float area_sqm
        string location_city
        string soil_type
        string sun_exposure
        string cultivation_method
        string mowing_method
        date blade_sharpened_at
        string grass_type
        int grass_seed_product_id FK
        string photo
        datetime created_at
        datetime updated_at
    }

    FertilizerProduct {
        int id PK
        string brand
        string product_name
        string npk
        float npk_n
        float npk_p
        float npk_k
        string fertilizer_type
        string season
        text description
    }

    FertilizingLog {
        int id PK
        int lawn_id FK
        date date
        int fertilizer_product_id FK
        string fertilizer_type
        float npk_n
        float npk_p
        float npk_k
        float amount_per_sqm
        string photo
        text notes
    }
```

---

## 3. 🌐 Végpontok és Útvonal-architektúra (`app.py`)

| Kategória | Végpont URL | HTTP Metódus | Leírás |
|---|---|---|---|
| **Hitelesítés** | `/login` | `GET, POST` | Bejelentkezés ("Emlékezz rám" támogatással) |
| | `/register` | `GET, POST` | Új felhasználói fiók létrehozása |
| | `/logout` | `GET` | Kijelentkezés |
| **Műszerfal** | `/` | `GET` | Időjárás, gyorsstatisztikák, javaslatok, gyepkártyák |
| **Gyep Profilok** | `/profiles` | `GET` | Felhasználó összes gyepének listája |
| | `/profiles/new` | `GET, POST` | Új gyep profil létrehozása fotóval és előzményekkel |
| | `/profiles/<id>` | `GET` | Részletes adatlap, előzmények, gyorsgombok |
| | `/profiles/<id>/edit` | `GET, POST` | Profil szerkesztése |
| | `/profiles/<id>/delete`| `POST` | Gyep és kapcsolódó naplók végleges törlése |
| **Tevékenységek** | `/activities` | `GET` | Tevékenységek szűrhető táblázata |
| | `/activities/add/<type>` | `GET, POST` | Új naplóbejegyzés rögzítése a megadott típushoz |
| **Tervezés** | `/calendar` | `GET` | Havi eseménynaptár navigációval |
| | `/suggestions` | `GET` | Prioritás szerint csoportosított intelligens tanácsok |
| **AJAX API** | `/api/grass-product/<id>` | `GET` | Fűmag adatok lekérése JSON formátumban |
| | `/api/fertilizer-product/<id>` | `GET` | Műtrágya NPK adatok lekérése JSON formátumban |
| | `/api/fertilizer-product/new` | `POST` | Új műtrágya azonnali mentése a katalógusba |

---

## 4. 🧠 Szabályalapú Javaslatmotor Logikája (`utils/suggestions.py`)

A javaslatmotor az alábbi szabályok mentén alkot személyre szabott ajánlásokat:

1. **Öntözés**:
   - Vizsgálja az utolsó öntözés óta eltelt napokat.
   - Súlyozza a talaj típusát: homokos talaj (~5 nap), vályogos talaj (~7 nap), agyagos/tőzeges talaj (~9–10 nap).
   - Figyelembe veszi az időjárást: ha az OpenWeatherMap szerint esett az eső (`rain_1h > 0`), az öntözés kihagyását javasolja.
   - Kiszámítja a szükséges vízmennyiséget a gyep méretére (pl. `150 m² × 2–2.5 liter = 300–375 liter`).
2. **Fűnyírás**:
   - Évszakonkénti ciklusok: tavasz (7 nap), nyár (10 nap), ősz (14 nap), tél (nincs nyírás).
   - Vágásmagasság-ajánlás: nyáron magasabbra (5–6 cm) a talaj kiszáradásának megakadályozására.
3. **Trágyázás**:
   - Tavasz: Nitrogéndús formula (pl. *ICL All Round 24-5-8*).
   - Nyár / Ősz: Káliumdús stresszkezelő formula (pl. *ICL Stress Control 16-5-22* vagy *Compo Herbst 4-5-20*).
   - Kiszámítja a javasolt kiszórási tömeget a teljes felületre (30–40 g/m²).
4. **Gyepszellőztetés & Szezonális gondozás**:
   - Tavaszi indítás (március–április) és őszi felkészítés (szeptember–október) időzítése.

---

## 5. 🛠️ Telepítés és Helyi Futtatás

### 1. Repository klónozása
```bash
git clone https://github.com/JosephWolf1986/GyepMester.git
cd GyepMester
```

### 2. Virtuális környezet létrehozása és aktiválása
```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### 3. Függőségek telepítése
```bash
pip install -r requirements.txt
```

### 4. Környezeti változók beállítása (`.env`)
Hozz létre egy `.env` fájlt a gyökérben (a `.env.example` alapján):
```env
SECRET_KEY=titkos-biztonsagi-kulcs-2026

# Helyi SQLite adatbázis:
DATABASE_URL=sqlite:///gyepmester.db

# VAGY PostgreSQL (pl. Supabase):
# DATABASE_URL=postgresql://postgres.YOUR_PROJECT:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require

# OpenWeatherMap API kulcs (opcionális az élő időjáráshoz):
OPENWEATHER_API_KEY=az_api_kulcsod
```

### 5. Alkalmazás indítása
```bash
python app.py
```
Az alkalmazás automatikusan létrehozza a táblákat és betölti az alaptermékeket az adatbázisba.

Nyisd meg a böngésződben:
👉 **`http://localhost:5000`**

---

## 📄 Licenc

Ez a projekt nyílt forráskódú, és szabadon használható saját célra és továbbfejlesztésre.
Készült a modern gyepápolás rajongóinak! 🌿
