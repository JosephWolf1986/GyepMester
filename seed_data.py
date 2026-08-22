"""
seed_data.py – Beépített termék katalógus feltöltése az adatbázisba.
Futtatás: python seed_data.py  VAGY az app.py automatikusan meghívja.
"""

from models import db, GrassSeedProduct, FertilizerProduct


# =============================================================================
# FŰMAG TERMÉKEK
# =============================================================================

GRASS_SEED_PRODUCTS = [
    # --- Barenbrug ---
    {
        "brand": "Barenbrug",
        "product_name": "Water Saver",
        "grass_types": "Nádképű csenkesz, Vörös csenkesz",
        "usage": "Szárazságtűrő",
        "description": "Kifejezetten szárazságtűrő keverék, mélyre hatoló gyökérzettel. "
                       "Ideális Magyarország egyre melegebb, szárazabb éghajlatán.",
    },
    {
        "brand": "Barenbrug",
        "product_name": "Resilient Blue",
        "grass_types": "Réti perje",
        "usage": "Általános / Strapabíró",
        "description": "Nagy ellenállóképességű pázsitfű, tarackoló réti perje alapú. "
                       "Napos, jól szellőzött területekre ideális.",
    },
    {
        "brand": "Barenbrug",
        "product_name": "BarPower RPR",
        "grass_types": "Angol perje, Réti perje",
        "usage": "Sport / Erős igénybevétel",
        "description": "Sportpályákra és nagy igénybevételnek kitett területekre ajánlott. "
                       "Kiváló regenerációs képesség.",
    },
    {
        "brand": "Barenbrug",
        "product_name": "Shadow Gazon",
        "grass_types": "Vörös csenkesz, Réti perje",
        "usage": "Árnyéktűrő",
        "description": "Speciálisan árnyékos helyekre fejlesztett keverék. "
                       "Akár 70%-os árnyékot is elvisel.",
    },
    # --- DLF Turfline ---
    {
        "brand": "DLF Turfline",
        "product_name": "Sport",
        "grass_types": "Angol perje, Réti perje",
        "usage": "Sport / Erős igénybevétel",
        "description": "Strapabíró, gyorsan regenerálódó keverék. Magas taposástűrés, "
                       "kiváló tömöttség.",
    },
    {
        "brand": "DLF Turfline",
        "product_name": "Ornamental – Díszgyep",
        "grass_types": "Vörös csenkesz, Réti perje, Csenkesz",
        "usage": "Díszgyep",
        "description": "Finom szálú, elegáns megjelenésű díszgyep keverék. "
                       "Alacsony vágási magasság mellett is szép marad.",
    },
    {
        "brand": "DLF Turfline",
        "product_name": "Grass Fix – Felülvető",
        "grass_types": "Angol perje, Réti perje",
        "usage": "Regeneráló / Felülvetés",
        "description": "Kopasz foltok javítására, felülvetésre ideális gyors kelésű keverék.",
    },
    # --- Eurogreen ---
    {
        "brand": "Eurogreen",
        "product_name": "Trockenrasen Mediterran",
        "grass_types": "Nádképű csenkesz, Angol csenkesz, Vörös csenkesz",
        "usage": "Szárazságtűrő / Mediterrán",
        "description": "Magas nádképű csenkesz tartalmú, víztakarékos keverék száraz, "
                       "napos területekre. Ideális Közép-Magyarország éghajlatán.",
    },
    {
        "brand": "Eurogreen",
        "product_name": "Gala",
        "grass_types": "Réti perje, Vörös csenkesz",
        "usage": "Díszgyep / Prémium",
        "description": "Prémium díszgyep keverék sűrű, homogén gyepszőnyeghez.",
    },
    {
        "brand": "Eurogreen",
        "product_name": "Park",
        "grass_types": "Angol perje, Réti perje, Vörös csenkesz",
        "usage": "Általános / Parki",
        "description": "Univerzális parki és kerti keverék, közepes igénybevételre. "
                       "Jó mérsékleti viszonyok között kiválóan teljesít.",
    },
    # --- Scotts EverGreen ---
    {
        "brand": "Scotts EverGreen",
        "product_name": "Family – Családi kert",
        "grass_types": "Angol perje, Réti perje",
        "usage": "Általános / Gyerekbarát",
        "description": "Strapabíró, taposástűrő keverék aktív, mozgalmas kertekbe. "
                       "Ideális, ahol gyerekek és állatok is vannak.",
    },
    {
        "brand": "Scotts EverGreen",
        "product_name": "Shade – Árnyéktűrő",
        "grass_types": "Vörös csenkesz",
        "usage": "Árnyéktűrő",
        "description": "Vörös csenkesz alapú keverék fák alatt, árnyékos területekre.",
    },
]


# =============================================================================
# MŰTRÁGYA TERMÉKEK
# =============================================================================

FERTILIZER_PRODUCTS = [
    # --- ICL Landscaper Pro ---
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "All Round",
        "npk": "24-5-8",
        "npk_n": 24.0, "npk_p": 5.0, "npk_k": 8.0,
        "fertilizer_type": "Nitrogéndús",
        "season": "Tavasz – Nyár",
        "description": "Általános célú, 4-5 hónapos hatású burkolt műtrágya. "
                       "Tavaszi-nyári fenntartáshoz ideális.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "Maintenance",
        "npk": "21-6-8",
        "npk_n": 21.0, "npk_p": 6.0, "npk_k": 8.0,
        "fertilizer_type": "Komplex",
        "season": "Tavasz – Nyár",
        "description": "Fenntartó műtrágya, 2-3 hónapos hatással. "
                       "Egyenletes növekedést biztosít.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "New Grass – Indító",
        "npk": "20-20-8",
        "npk_n": 20.0, "npk_p": 20.0, "npk_k": 8.0,
        "fertilizer_type": "Indító (P-dús)",
        "season": "Telepítéskor / Felülvetéskor",
        "description": "Magas foszfortartalmú indítótrágya új gyep telepítéséhez "
                       "és felülvetéshez. Elősegíti a gyökérképződést.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "Spring & Summer",
        "npk": "20-0-7",
        "npk_n": 20.0, "npk_p": 0.0, "npk_k": 7.0,
        "fertilizer_type": "Nitrogéndús",
        "season": "Tavasz – Nyár",
        "description": "Foszformentes, nitrogéntúlsúlyos tavaszi-nyári formula. "
                       "Intenzív zöldülés és növekedés.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "Stress Control",
        "npk": "16-5-22",
        "npk_n": 16.0, "npk_p": 5.0, "npk_k": 22.0,
        "fertilizer_type": "Káliumdús / Stressztűrő",
        "season": "Nyár – Ősz",
        "description": "Magas káliumtartalmú (16-5-22), burkolt stresszkezelő műtrágya. "
                       "Megerősíti a növényi sejtfalakat és felkészíti a gyepet a nyári hőséggel, "
                       "szárazsággal vagy a téli faggyal szemben. Hatástartam: 2-3 hónap.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "Full Season",
        "npk": "27-5-5",
        "npk_n": 27.0, "npk_p": 5.0, "npk_k": 5.0,
        "fertilizer_type": "Nitrogéndús",
        "season": "Egész szezon (8-9 hónap)",
        "description": "Hosszú hatású (8-9 hónap) egész szezonos műtrágya. "
                       "Egyetlen alkalmazás az egész évre.",
    },
    {
        "brand": "ICL Landscaper Pro",
        "product_name": "Shade Special – Árnyék",
        "npk": "11-5-5",
        "npk_n": 11.0, "npk_p": 5.0, "npk_k": 5.0,
        "fertilizer_type": "Komplex",
        "season": "Tavasz – Ősz",
        "description": "Árnyékos gyepfelületekre kifejlesztett, kiegyensúlyozott formula "
                       "nyomelem-kiegészítéssel.",
    },
    # --- Compo ---
    {
        "brand": "Compo",
        "product_name": "Rasen-Langzeitdünger – Hosszú hatású",
        "npk": "14-4-8",
        "npk_n": 14.0, "npk_p": 4.0, "npk_k": 8.0,
        "fertilizer_type": "Hosszú hatású / Komplex",
        "season": "Tavasz",
        "description": "Compo hosszú hatású (3 hónapos) gyeptrágya egyenletes "
                       "tápanyagleadással. Nem éget.",
    },
    {
        "brand": "Compo",
        "product_name": "Herbst-Rasendünger – Őszi",
        "npk": "4-5-20",
        "npk_n": 4.0, "npk_p": 5.0, "npk_k": 20.0,
        "fertilizer_type": "Káliumdús",
        "season": "Ősz",
        "description": "Magas káliumtartalmú őszi trágya a gyökerek erősítésére "
                       "és a téliesítésre. Növeli a fagytűrést.",
    },
    # --- Genezis (Nitrogénművek) ---
    {
        "brand": "Genezis",
        "product_name": "Gyepstarter",
        "npk": "15-15-15",
        "npk_n": 15.0, "npk_p": 15.0, "npk_k": 15.0,
        "fertilizer_type": "Komplex / Indító",
        "season": "Telepítéskor",
        "description": "Kiegyensúlyozott NPK arányú indítótrágya új gyephez. "
                       "Magyar gyártású, megbízható minőség.",
    },
    {
        "brand": "Genezis",
        "product_name": "Gyep Nitro",
        "npk": "26-0-0",
        "npk_n": 26.0, "npk_p": 0.0, "npk_k": 0.0,
        "fertilizer_type": "Nitrogéndús",
        "season": "Tavasz – Kora nyár",
        "description": "Tiszta nitrogén alapú trágya gyors zöldüléshez. "
                       "Tavaszi indításhoz, mértékkel alkalmazva.",
    },
    # --- T.Garden ---
    {
        "brand": "T.Garden",
        "product_name": "Gyeptrágya Tavasz",
        "npk": "20-5-10",
        "npk_n": 20.0, "npk_p": 5.0, "npk_k": 10.0,
        "fertilizer_type": "Nitrogéndús",
        "season": "Tavasz",
        "description": "Szabályozott tápanyagleadású tavaszi gyeptrágya. "
                       "Serkenti a növekedést, erősíti a gyepsűrűséget.",
    },
    {
        "brand": "T.Garden",
        "product_name": "Gyeptrágya Ősz",
        "npk": "8-5-20",
        "npk_n": 8.0, "npk_p": 5.0, "npk_k": 20.0,
        "fertilizer_type": "Káliumdús",
        "season": "Ősz",
        "description": "Magas káliumtartalmú őszi formula a téli felkészüléshez. "
                       "Erősíti a gyökereket és növeli az ellenállóképességet.",
    },
]


def seed_products(app):
    """Feltölti az adatbázist a beépített termék katalógussal (hiányzó elemek beszúrása)."""
    with app.app_context():
        added_seeds = 0
        for data in GRASS_SEED_PRODUCTS:
            exists = GrassSeedProduct.query.filter_by(
                brand=data['brand'], product_name=data['product_name']
            ).first()
            if not exists:
                db.session.add(GrassSeedProduct(**data))
                added_seeds += 1

        added_ferts = 0
        for data in FERTILIZER_PRODUCTS:
            exists = FertilizerProduct.query.filter_by(
                brand=data['brand'], product_name=data['product_name']
            ).first()
            if not exists:
                db.session.add(FertilizerProduct(**data))
                added_ferts += 1

        if added_seeds > 0 or added_ferts > 0:
            db.session.commit()
            print(f"[OK] Katalógus frissítve: +{added_seeds} fűmag, +{added_ferts} műtrágya.")
        else:
            print("[OK] A termék katalógus naprakész.")
