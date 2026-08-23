# 🌿 GyepMester – Rendszerdokumentáció és Architektúra Összefoglaló

A **GyepMester** egy okos, személyre szabott webes gyepápolási és kertgondozási naplózó rendszer. Segítségével a felhasználók nyilvántarthatják kertjeik/gyepjeik paramétereit, naplózhatják a gondozási műveleteket (öntözés, fűnyírás, trágyázás, gyepszellőztetés, gyomirtás, kártevőirtás), valamint intelligens, időjárás- és évszakfüggő javaslatokat kapnak az optimális gyepápoláshoz.

---

## 1. 🏗️ Rendszerarchitektúra és Mappastruktúra

Az alkalmazás a klasszikus **MVC (Model-View-Controller)** mintára épülő Flask architektúrát valósít meg, kiszolgáló oldali Jinja2 sablonozással és modern Vanilla CSS/JS alapú interaktív felülettel.

```
GyepMester/
│
├── app.py                     # Alkalmazás belépési pont, URL útvonalak, kontrollerek
├── config.py                  # Konfiguráció (adatbázis, fájlfeltöltés, API kulcsok)
├── models.py                  # SQLAlchemy adatmodellek és relációk
├── seed_data.py               # Beépített fűmag- és műtrágya-katalógus inicializáló
├── requirements.txt           # Python függőségek listája
├── README.md                  # Rendszerdokumentáció
│
├── utils/                     # Üzleti logika és segédmodulok
│   ├── helpers.py             # Képfeldolgozás (Pillow, WebP, EXIF), dátum kalkulációk
│   ├── suggestions.py         # Intelligens szabálymotor (ápolási javaslatok generálása)
│   └── weather.py             # OpenWeatherMap API integráció (aktuális + előrejelzés)
│
├── static/                    # Statikus erőforrások
│   ├── css/
│   │   └── style.css          # Prémium sötét témájú CSS design tokens rendszer
│   ├── js/
│   │   └── main.js            # Frontend interakciók, AJAX termék-kitöltő, naptár motor
│   └── uploads/               # Feltöltött és optimalizált felhasználói fotók
│
└── templates/                 # Jinja2 HTML sablonok
    ├── base.html              # Fő layout (oldalsáv, felhasználói sáv, flash értesítések)
    ├── dashboard.html         # Főoldali összefoglaló műszerfal
    ├── suggestions.html       # Priorizált javaslatok gyepenként
    ├── calendar.html          # Interaktív havi ápolási naptár
    ├── auth/                  # Bejelentkezés és regisztráció
    │   ├── login.html
    │   └── register.html
    ├── profile/               # Gyep profilok CRUD felülete
    │   ├── list.html
    │   ├── new.html           # Új gyep felvétele (művelés, nyírás, tápanyag- és kés-előzmények)
    │   ├── detail.html        # Részletes adatlap és gyorsműveletek
    │   └── edit.html          # Profil szerkesztése
    ├── activities/            # Tevékenységnaplózás (6 típus)
    │   ├── list.html
    │   └── add.html
    └── errors/                # Egyedi hibaoldalak
        ├── 403.html
        └── 404.html
```

---

## 2. 🗄️ Adatmodell és Adatbázis Architektúra

Az adatbázis kezelését a **Flask-SQLAlchemy** ORM végzi (alapértelmezetten SQLite motorral, de PostgreSQL/MySQL-re is átirányítható a `DATABASE_URL` környezeti változóval).

### Mermaid Adatbázis ER-Diagram:

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
        string username
        string email
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

### Entitások és szerepük:
1. **User**: Felhasználói fiókok kezelése, jelszóhashelés (`werkzeug.security`).
2. **LawnProfile**: Egy-egy adott gyepfelület fizikai és gondozási paraméterei:
   - Alapadatok: név, terület (m²), helyszín (város), talajtípus, napsütés kitettség, fotó.
   - **Művelés módja (`cultivation_method`)**: `Extenzív`, `Normál`, `Intenzív`.
   - **Nyírás módja (`mowing_method`)**: `Kézi`, `Gépi (fűnyíró)`.
   - **Késélezési előzmény (`blade_sharpened_at`)**: A fűnyírókés legutóbbi élezésének dátuma.
   - Fűtípus / Fűmag termék kapcsolat.
3. **GrassSeedProduct & FertilizerProduct**: Beépített katalógusok (pl. *Barenbrug, DLF Turfline, ICL, COMPO, Genezis, T.Garden*), amelyekből automatikusan kitölthetők a fajták és N-P-K arányok. A felhasználók a felületen menet közben új termékeket is felvehetnek a katalógusba.
4. **Napló Entitások** (*WateringLog, MowingLog, FertilizingLog, AerationLog, WeedLog, PestLog*): Események időpontjai, számszerű adatai (vágásmagasság cm, vízmennyiség l/m², kiszórt g/m², súlyosság), megjegyzések és képmellékletek.

---

## 3. 🧠 Intelligens Funkciók és Üzleti Logika

### A) Szabályalapú Javaslatmotor (`utils/suggestions.py`)
A javaslatmotor dinamikusan értékeli az egyes gyepterületek állapotát és a következő szempontok alapján állít elő teendőket:
- **Öntözés**:
  - Figyelembe veszi az utolsó öntözés óta eltelt napokat.
  - Súlyozza a talajtípust (pl. a homokos talaj 5 naponta, az agyagos 9 naponta igényel öntözést).
  - Évszak és időjárás érzékenység: ha az OpenWeather API szerint esett az eső (`rain_1h > 0`), a rendszer jelzi, hogy az öntözés kihagyható.
  - Riasztási szintek: `low`, `medium`, `high` (sürgős kiszáradásveszély esetén azonnali liter-kalkulációval a területre számolva).
- **Fűnyírás**: Évszakonként eltérő vágási ciklusokat és optimális fűmagasságot ajánl (pl. nyári hőségben 5–6 cm a talaj árnyékolására, tavasszal 4–5 cm).
- **Trágyázás**: Évszakhoz illeszkedő tápanyag-összetételt (tavasszal nitrogéndús, ősszel fagyállóságot javító káliumdús) és pontos gramm-mennyiséget javasol a gyep területe alapján.
- **Gyepszellőztetés & Szezonális tippek**: Időzíti a március–áprilisi tavaszi indítást, a szeptemberi őszi regenerálást, valamint a téli taposásvédelmet.

### B) Új Gyep Létrehozása & Előzménykezelés
Gyep felvételekor az alapadatokon kívül azonnal rögzíthetők:
- **Művelési és nyírási beállítások** (vizuális kártyaválasztókkal).
- **Tápanyag előzmény**: Megadható az utolsó trágyázás dátuma, és kiválasztható a termék a katalógusból, vagy kézzel rögzíthető. Mentéskor a rendszer automatikusan létrehozza a gyep első `FertilizingLog` naplóbejegyzését.
- **Dinamikus műtrágya felvétel**: Ha a keresett műtrágya nincs a listában, az űrlapon belüli AJAX panellel azonnal hozzáadható az adatbázishoz, és rögtön kiválaszthatóvá válik.
- **Fűnyírókés élezési dátum**: Későbbi emlékeztetők és karbantartás nyomon követésére.

### C) Időjárás Integráció (`utils/weather.py`)
- Lekéri az adott város pillanatnyi hőmérsékletét, páratartalmát, szélsebességét és csapadékadatait az **OpenWeatherMap API**-n keresztül.
- Visszaadja a formázott adatokat és ikonokat a Dashboard és Javaslatok moduloknak.

### D) Robusztus Médiafeldolgozó (`utils/helpers.py`)
- Képfeltöltéskor a Pillow (PIL) könyvtár automatikusan:
  - Átméretezi a nagy felbontású fotókat maximum 1200×1200 képpontra.
  - Kezeli és javítja a mobiltelefonok EXIF tájolási információit (elkerülve a fejjel lefelé elforduló képeket).
  - WebP formátumba tömöríti a fájlokat, minimalizálva a hálózati sávszélességet és a tárhelyhasználatot.
  - Gyep törlésekor vagy fotócserénél automatikusan törli az árva fájlokat a lemezről.

---

## 4. 🌐 Végpontok és Útvonal-architektúra (`app.py`)

| Kategória | Végpont URL | Metódus | Leírás |
|---|---|---|---|
| **Autentikáció** | `/login` | `GET, POST` | Bejelentkezés ("Emlékezz rám" opcióval) |
| | `/register` | `GET, POST` | Új felhasználó regisztrációja |
| | `/logout` | `GET` | Munkamenet lezárása |
| **Dashboard** | `/` | `GET` | Időjárás, gyorsstatisztikák, sürgős teendők |
| **Gyep Profilok** | `/profiles` | `GET` | Felhasználó gyepjeinek listája |
| | `/profiles/new` | `GET, POST` | Új profil létrehozása fotóval, előzményekkel és beállításokkal |
| | `/profiles/<id>` | `GET` | Részletes adatlap, előzmények, gyorsgombok |
| | `/profiles/<id>/edit` | `GET, POST` | Profil és beállítások módosítása |
| | `/profiles/<id>/delete`| `POST` | Profil és kapcsolódó naplók végleges törlése |
| **Tevékenységek** | `/activities` | `GET` | Szűrhető napló (öntözés, nyírás, stb.) |
| | `/activities/add/<type>` | `GET, POST` | Új bejegyzés rögzítése a kiválasztott típushoz |
| **Tervezés** | `/calendar` | `GET` | Havi naptár havi navigációval és színkódolt eseményekkel |
| | `/suggestions` | `GET` | Részletes, csoportosított tanácsok gyepenként |
| **AJAX API** | `/api/grass-product/<id>` | `GET` | Fűmag termékadatok JSON-ben (űrlap auto-kitöltés) |
| | `/api/fertilizer-product/<id>` | `GET` | Műtrágya NPK adatok JSON-ben (űrlap auto-kitöltés) |
| | `/api/fertilizer-product/new` | `POST` | Új műtrágya termék azonnali mentése a katalógusba |

---

## 5. 🎨 Frontend és Felhasználói Élmény (UI/UX)

- **Design System (`static/css/style.css`)**:
  - Modern mélysötét (`#0a0f0d`, `#111a14`) háttér, organikus fűzöld és smaragd kiemelésekkel (`#22c55e`, `#16a34a`).
  - Google Fonts tipográfia: *Outfit* a címekhez és *Inter* az adatokhoz/törzsszövegekhez.
  - Vizuális rádiógomb-kártyák (`.method-selector`, `.method-card`) a művelési és nyírási módok intuitív kiválasztásához.
  - Teljesen reszponzív: asztali gépen fix oldalsáv, tableten kompakt ikon-nézet, mobilon alsó/felső igazítás.
- **Dinamikus Interakciók (`static/js/main.js` & inline scriptek)**:
  - **Auto-Kitöltés**: Termék kiválasztásakor (pl. fűmag vagy műtrágya) aszinkron `fetch()` kéréssel lekéri a tulajdonságokat és kitölti a mezőket.
  - **Dinamikus Termék Mentés**: Új műtrágya létrehozása az űrlap elhagyása nélkül, NPK előnézettel.
  - **Azonnali Kép-előnézet**: Fájl kiválasztásakor még a szerverre küldés előtt megjeleníti a fotót.
  - **Önmegsemmisítő Értesítések**: A flash üzenetek 5 másodperc után animáltan eltűnnek.
  - **Naptár Renderelés**: Tiszta JavaScript generálja le a havi naprácsot, elhelyezve a színkódolt esemény-jelölőket.

---

## 6. 🚀 Telepítési és Üzemeltetési Útmutató

### 1. Függőségek telepítése
```bash
# Virtuális környezet aktiválása után:
pip install -r requirements.txt
```

### 2. Környezeti változók (.env) beállítása (Opcionális)
Hozz létre egy `.env` fájlt a gyökérkönyvtárban:
```env
SECRET_KEY=egyedi-titkos-kulcs

# Helyi SQLite:
DATABASE_URL=sqlite:///gyepmester.db

# VAGY Supabase PostgreSQL:
# DATABASE_URL=postgresql://postgres.PROJECT_REF:JELSZO@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require

OPENWEATHER_API_KEY=az_openweather_api_kulcsod
```

### 3. Alkalmazás futtatása
```bash
python app.py
```
Az alkalmazás automatikusan inicializálja az adatbázist (`db.create_all()`), betölti a katalógusadatokat a `seed_data.py`-ból, és elérhetővé válik a böngészőben:
👉 **`http://localhost:5000`**
