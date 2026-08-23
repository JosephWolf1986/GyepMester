"""utils/suggestions.py – Javaslat generáló motor."""
from datetime import date, timedelta


# Gyep gondozási intervallumok (napokban)
INTERVALS = {
    'watering': {
        'default': 7,           # Átlagosan heti 1-2x
        'summer': 4,            # Nyáron sűrűbben
        'warning': 10,          # Ennyi nap után már riasztás
        'Homokos': 5,           # Homokos talaj gyorsabban szárad
        'Agyagos': 9,
        'Vályogos': 7,
        'Tőzeges': 10,
    },
    'mowing': {
        'spring': 7,            # Tavasz: hetente
        'summer': 10,           # Nyár: kicsit ritkábban
        'autumn': 14,           # Ősz: ritkábban
        'warning': 21,          # 3 hét után riasztás
    },
    'fertilizing': {
        'spring': 60,           # Tavaszi trágyázás
        'summer': 90,
        'autumn': 90,           # Őszi trágyázás
        'warning': 120,
    },
    'aeration': {
        'per_year': 2,          # Évente 2x (tavasz + ősz)
    },
}

SEASON_MAP = {
    (3, 4, 5): 'spring',
    (6, 7, 8): 'summer',
    (9, 10, 11): 'autumn',
    (12, 1, 2): 'winter',
}


def get_season():
    month = date.today().month
    for months, season in SEASON_MAP.items():
        if month in months:
            return season
    return 'spring'


def calculate_mowing_plan(lawn, weather=None):
    """
    Intelligens fűnyírási ajánló motor.
    Kiszámítja az optimális nyírási gyakoriságot és vágásmagasságot:
    1. Évszak & Hőmérséklet
    2. Fűmag / Fűtípus összetétel
    3. Talajtípus & Vízgazdálkodás
    4. Művelési mód (Extenzív/Normál/Intenzív)
    5. Trágyázási előzmények & NPK hatásmechanizmus (Growth Surge)
    """
    today = date.today()
    season = get_season()
    stage = lawn.lawn_stage or 'Meglévő, beállt gyep'

    # ─────────────────────────────────────────────────────────────────────────
    # 1. PROTOKOLL: VETÉS ELŐTT ÁLL
    # ─────────────────────────────────────────────────────────────────────────
    if stage == 'Vetés előtt áll':
        return {
            'stage': 'before_seed',
            'stage_badge': '🚜 Vetés előtti fázis',
            'interval_days': None,
            'frequency_label': 'Nincs nyírás (magágy készítés)',
            'recommended_height_cm': '–',
            'days_since_mow': None,
            'due_in': None,
            'status': 'prep',
            'status_label': 'Fűnyírás nem szükséges',
            'status_color': 'gray',
            'reasoning': [
                '🚜 A terület még vetés előtt áll, nincs nyírandó fűállomány.',
                '🌱 Fókuszálj a gyommentesítésre, talajlazításra és a magágy előkészítésére.',
            ],
            'fertilizer_impact': None,
            'weather_warning': None,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 2. PROTOKOLL: FRISS VETÉS / FELÜLVETÉS
    # ─────────────────────────────────────────────────────────────────────────
    if stage == 'Friss vetés / Felülvetés':
        days_since_seed = None
        if lawn.seeding_date:
            days_since_seed = (today - lawn.seeding_date).days

        if days_since_seed is not None and days_since_seed >= 25:
            # Első kímélő vágás fázisa
            last_m = lawn.last_mowing()
            return {
                'stage': 'fresh_seed',
                'stage_badge': f'🌿 Friss vetés: Első kímélő vágás ({days_since_seed}. nap)',
                'interval_days': 7,
                'frequency_label': 'Kímélő első nyírás (7–8 naponta)',
                'recommended_height_cm': '5.5 – 6.5',
                'days_since_mow': days_since(last_m.date) if last_m and last_m.date else None,
                'due_in': 0,
                'status': 'first_cut',
                'status_label': 'Első kímélő vágás esedékes',
                'status_color': 'warning',
                'reasoning': [
                    f'🌱 A vetés elérte a {days_since_seed}. napot. Ha a fű elérte a 7–8 cm-es magasságot, elvégezhető az első kímélő nyírás.',
                    '✂️ Kizárólag borotvaéles fűnyírókéssel vágj! Az életlen kés kitépi a még gyenge gyökérzetű fiatal szálakat.',
                    '📏 Magas tarló: Csak a legfelső 1/3-ot csípd le, hagyd a tarlót 5.5–6.0 cm magasan.',
                    '🚫 A fűnyíróval óvatosan fordulj, ne kapartasd meg a kerekeket a laza magágyon.',
                ],
                'fertilizer_impact': None,
                'weather_warning': None,
            }
        else:
            # Kelési fázis: Nyírás tilos!
            days_str = f"({days_since_seed}. nap)" if days_since_seed is not None else ""
            return {
                'stage': 'fresh_seed',
                'stage_badge': f'🌿 Friss vetés {days_str}: Fűnyírás tilos!',
                'interval_days': None,
                'frequency_label': 'Tilos a nyírás (kelési időszak)',
                'recommended_height_cm': 'Megvárni a 7–8 cm-t',
                'days_since_mow': None,
                'due_in': 999,
                'status': 'no_mow',
                'status_label': 'Fűnyírás szigorúan tilos!',
                'status_color': 'danger',
                'reasoning': [
                    '⛔ Nyírási tilalom: A csírázó fűszálak gyökérzete még rendkívül sekély és gyenge. A fűnyíró kése és huzata kitépné a csíranövényeket.',
                    '🚜 Talajtömörödés megelőzése: Ne lépj a magágyra és ne tolj rá nehéz fűnyírót a talaj egyenletességének megőrzéséhez.',
                    '⏱️ Mikor szabad először nyírni? Amikor a fűszálak elérik a 7–8 cm-es magasságot (általában a vetést követő 3–4. héten).',
                ],
                'fertilizer_impact': None,
                'weather_warning': None,
            }

    # ─────────────────────────────────────────────────────────────────────────
    # 3. PROTOKOLL: MEGLÉVŐ, BEÁLLT GYEP
    # ─────────────────────────────────────────────────────────────────────────
    # Téli időszak kezelése
    if season == 'winter':
        return {
            'stage': 'established',
            'stage_badge': '🏡 Meglévő, beállt gyep',
            'interval_days': 30,
            'frequency_label': 'Téli pihenő (nem igényel nyírást)',
            'recommended_height_cm': '4.5 – 5.0',
            'days_since_mow': days_since(lawn.last_mowing().date) if lawn.last_mowing() else None,
            'due_in': 999,
            'status': 'dormant',
            'status_label': 'Téli nyugalmi időszak',
            'status_color': 'gray',
            'reasoning': ['Télen a gyep vegetációja leáll, a fűnyírás tavaszig szünetel a fagyvédelem miatt.'],
            'fertilizer_impact': None,
            'weather_warning': None,
        }

    # 1. Bázis intervallum (napokban) évszak szerint
    base_intervals = {
        'spring': 6.0,
        'summer': 7.5,
        'autumn': 9.0,
    }
    interval = base_intervals.get(season, 7.0)
    recommended_height = season_height(season)
    reasons = []

    # 2. Művelési mód hatása
    cult = lawn.cultivation_method or 'Normál'
    if cult == 'Intenzív':
        interval -= 2.0
        reasons.append('💪 Intenzív művelés: Szigorú 1/3-os vágási szabály a prémium tömöttségért.')
        recommended_height = '3.5 – 4.5' if season != 'summer' else '4.5 – 5.0'
    elif cult == 'Extenzív':
        interval += 3.0
        reasons.append('🌾 Extenzív művelés: Természetközeli állapot, ritkább vágási ciklus.')
        recommended_height = '5.0 – 6.5'
    else:
        reasons.append('🌿 Normál művelés: Kiegyensúlyozott gondozási ütem.')

    # 3. Fűtípus / Fűmag fajta hatása
    grass_str = f"{lawn.grass_type or ''} {lawn.seed_product.product_name if lawn.seed_product else ''} {lawn.seed_product.grass_types if lawn.seed_product else ''}".lower()

    if any(k in grass_str for k in ['angol perje', 'sport', 'rpr', 'gyors', 'power']):
        interval -= 1.0
        reasons.append('⚽ Gyors növekedésű fűfajta (pl. Angol perje / Sport): Intenzív hajtásképződés, gyakoribb vágást igényel.')
    elif any(k in grass_str for k in ['vörös csenkesz', 'árnyék', 'shade', 'díszgyep', 'ornamental', 'finom']):
        interval += 1.0
        reasons.append('🌳 Finom szálú / árnyéktűrő fajta (pl. Vörös csenkesz): Mérsékeltebb növekedési ütem.')
    elif any(k in grass_str for k in ['nádképű', 'water saver', 'trockenrasen', 'mediterran']):
        if season == 'summer':
            reasons.append('☀️ Nádképű csenkesz: Kiváló szárazságtűrés, nyáron érdemes magasabbra hagyni (5.5–6.5 cm).')
            recommended_height = '5.5 – 6.5'

    # 4. Talajtípus hatása
    soil = lawn.soil_type or ''
    if soil in ['Vályogos', 'Tőzeges']:
        interval -= 0.5
        reasons.append(f'🌱 {soil} talaj: Jó tápanyag- és vízmegtartó képesség, ami serkenti a folyamatos növekedést.')
    elif soil == 'Homokos':
        interval += 0.5
        reasons.append('🏖️ Homokos talaj: Gyorsabban szárad és kimosódik a tápanyag, mérsékeltebb növekedési erély.')

    # 5. Trágyázási előzmények & NPK hatásmechanizmus
    last_fert = lawn.last_fertilizing()
    fert_impact = None
    if last_fert and last_fert.date:
        fert_days = (today - last_fert.date).days
        fert_name = last_fert.fertilizer_product.product_name if last_fert.fertilizer_product else (last_fert.fertilizer_type or 'Műtrágya')
        npk_n = last_fert.npk_n or 0
        npk_k = last_fert.npk_k or 0

        # Nitrogéndús műtrágya elemzése
        if npk_n >= 18 or 'nitro' in (last_fert.fertilizer_type or '').lower() or 'all round' in fert_name.lower():
            if 7 <= fert_days <= 28:
                interval -= 2.0
                fert_impact = {
                    'level': 'surge',
                    'badge': '🚀 Csúcsnövekedési fázis (Growth Surge)',
                    'text': f'{fert_days} napja kijuttatott nitrogéndús trágyázás ({fert_name}). Erőteljes vegetatív hajtásképződés!'
                }
                reasons.append(f'🚀 Nitrogén hatás ({fert_name}, {fert_days}. nap): Csúcsnövekedés! Nyírd sűrűbben, hogy elkerüld a tarló besárgulását (skalpolás)!')
            elif fert_days < 7:
                fert_impact = {
                    'level': 'absorbing',
                    'badge': '⏳ Tápanyag beépülési fázis',
                    'text': f'{fert_days} napja trágyázva ({fert_name}). A növekedési ugrás pár napon belül várható.'
                }
                reasons.append(f'⏳ Trágyázás után ({fert_days}. nap): A tápanyag felvétele folyamatban van, hamarosan felgyorsul a növekedés.')
            elif 29 <= fert_days <= 60:
                interval -= 0.5
                fert_impact = {
                    'level': 'active',
                    'badge': '🌱 Aktív tápanyaghatás',
                    'text': f'{fert_days} napja trágyázva ({fert_name}). Kiegyensúlyozott fenntartó növekedés.'
                }
                reasons.append(f'🌱 Tartós tápanyaghatás ({fert_name}, {fert_days}. nap): Egyenletes növekedési ütem.')
            elif fert_days > 90:
                interval += 1.0
                fert_impact = {
                    'level': 'depleted',
                    'badge': '⚠️ Kimerült tápanyagszint',
                    'text': f'{fert_days} napja nem volt trágyázva. A növekedés lelassult, tápanyag-utánpótlás javasolt.'
                }
                reasons.append(f'⚠️ Tápanyag kimerülés ({fert_days} napja nem volt trágyázás): A növekedés lassul, a gyep megritkulhat.')
        # Káliumdús / Stressztűrő trágya
        elif npk_k >= 18 or 'stress' in fert_name.lower() or 'kálium' in (last_fert.fertilizer_type or '').lower() or 'herbst' in fert_name.lower():
            fert_impact = {
                'level': 'stress_protection',
                'badge': '🛡️ Stresszvédelem & Erős sejtfalak',
                'text': f'{fert_days} napja kijuttatott káliumdús formula ({fert_name}). Erősíti a sejtfalakat, nem hajtatja túl a füvet.'
            }
            reasons.append(f'🛡️ Káliumdús védelem ({fert_name}): Nem hajtatja túl a lombot, növeli az ellenállóképességet.')
            if season == 'summer':
                recommended_height = '5.5 – 6.5'
    else:
        reasons.append('ℹ️ Nincs korábbi trágyázási bejegyzés rögzítve.')

    # 6. Időjárás hatása
    weather_warning = None
    if weather:
        temp = weather.get('temp', 20)
        rain_1h = weather.get('rain_1h', 0)

        if rain_1h > 0:
            weather_warning = '🌧️ Jelenleg esik az eső vagy vizes a gyep! Halaszd el a nyírást a fűszálak felszáradásáig, elkerülve a roncsolást és a gombásodást.'
            reasons.append('🌧️ Csapadékos idő: Vizes fű nyírása tilos (eltömi a fűnyírót, tépi a fűszálakat).')

        if 15 <= temp <= 24:
            interval -= 1.0
            reasons.append(f'🌡️ Ideális hőmérséklet ({temp:.1f}°C): A pázsitfűfélék számára optimális vegetációs tartomány.')
        elif temp >= 30:
            interval += 2.0
            recommended_height = '5.5 – 6.5'
            reasons.append(f'🔥 Nyári kánikula ({temp:.1f}°C): Hőségstressz miatt a növekedés lelassul. Hagyd magasabbra ({recommended_height} cm) a talaj árnyékolása érdekében!')
        elif temp < 10:
            interval += 3.0
            reasons.append(f'❄️ Hűvös idő ({temp:.1f}°C): Lassú anyagcsere, a nyírás ritkábban esedékes.')

    # Intervallum kerekítése és határok (min 2, max 14 nap)
    final_interval = max(2, min(14, int(round(interval))))

    # Szöveges gyakorisági címke
    if final_interval <= 3:
        frequency_label = 'Hetente 2-3 alkalommal (2–3 naponta)'
    elif final_interval <= 4:
        frequency_label = 'Hetente 2 alkalommal (3–4 naponta)'
    elif final_interval <= 6:
        frequency_label = 'Hetente 1-2 alkalommal (5–6 naponta)'
    elif final_interval <= 8:
        frequency_label = 'Hetente 1 alkalommal (7–8 naponta)'
    else:
        frequency_label = f'{final_interval}–{final_interval+2} naponta (Ritka ciklus)'

    # Esedékesség számítása
    last_mowing = lawn.last_mowing()
    if last_mowing and last_mowing.date:
        days_since_mow = (today - last_mowing.date).days
        due_in = final_interval - days_since_mow
    else:
        days_since_mow = 999
        due_in = -999

    if days_since_mow == 999:
        status = 'no_data'
        status_label = 'Még nincs korábbi nyírás'
        status_color = 'gray'
    elif due_in < -3:
        status = 'severely_overdue'
        status_label = f'Sürgős: {days_since_mow} napja nem volt nyírás!'
        status_color = 'danger'
    elif due_in < 0:
        status = 'overdue'
        status_label = f'Esedékes ({-due_in} napja esedékes)'
        status_color = 'danger'
    elif due_in == 0:
        status = 'due_today'
        status_label = 'Ma esedékes a fűnyírás!'
        status_color = 'warning'
    elif due_in <= 2:
        status = 'due_soon'
        status_label = f'{due_in} nap múlva esedékes'
        status_color = 'info'
    else:
        status = 'ok'
        status_label = f'Rendben ({due_in} nap múlva esedékes)'
        status_color = 'success'

    return {
        'interval_days': final_interval,
        'frequency_label': frequency_label,
        'recommended_height_cm': recommended_height,
        'days_since_mow': days_since_mow if days_since_mow != 999 else None,
        'due_in': due_in if days_since_mow != 999 else None,
        'status': status,
        'status_label': status_label,
        'status_color': status_color,
        'reasoning': reasons,
        'fertilizer_impact': fert_impact,
        'weather_warning': weather_warning,
    }


def calculate_watering_plan(lawn, weather=None):
    """
    Intelligens öntözési ajánló motor.
    Figyelembe veszi:
    1. Gyep állapota (Vetés előtt áll, Friss vetés / Felülvetés, Meglévő, beállt gyep)
    2. Vetés dátuma (Kelési időszak 0-21 nap visszaszámlálás)
    3. Időjárás (Hőmérséklet, Eső, Páratartalom, Szél)
    4. Talajtípus (Homokos, Agyagos, Vályogos, Tőzeges)
    5. Napsütés / Kitettség (Teljes nap, Félárnyas, Árnyékos)
    6. Fűmagfajta gyökérzónája (Nádképű mély gyökérzet vs Angol/Réti perje vs Csenkesz)
    7. Friss trágyázási bemosási riasztás (<48 óra)
    8. Teljes vízmennyiség kalkuláció (l/m2 és gyep össz liter / m3)
    """
    today = date.today()
    season = get_season()
    stage = lawn.lawn_stage or 'Meglévő, beállt gyep'
    area = lawn.area_sqm or 100.0

    # ─────────────────────────────────────────────────────────────────────────
    # 1. PROTOKOLL: VETÉS ELŐTT ÁLL (MAGÁGY ELŐKÉSZÍTÉS)
    # ─────────────────────────────────────────────────────────────────────────
    if stage == 'Vetés előtt áll':
        total_l = int(round(area * 18.0))
        return {
            'stage': 'before_seed',
            'stage_badge': '🚜 Magágy előkészítési fázis',
            'interval_days': 2,
            'frequency_label': 'Vetés előtt 1-2 nappal alapos beáztatás',
            'water_amount_l_per_sqm': '15 – 20',
            'total_liters': total_l,
            'total_m3': round(total_l / 1000.0, 1),
            'recommended_time': 'Reggel vagy kora délután',
            'days_since_water': None,
            'due_in': None,
            'status': 'prep',
            'status_label': 'Magágy beáztatás szükséges',
            'status_color': 'info',
            'fertilizer_flush_required': False,
            'weather_warning': None,
            'reasoning': [
                '🌱 Magágy előnedvesítés: A magok elszórása előtt 1-2 nappal áztasd be a talajt 15–20 l/m² vízzel, hogy a magágy alatti rétegek is nedvesek legyenek.',
                '🚜 A vetés napján a talaj teteje már legyen szikkadt, de mélyen nyirkos – így a magok nem tapadnak a hengerhez vagy cipőtalpra.',
                '⚠️ Ha Starter indító műtrágyát használsz, azt a magágy felső rétegébe dolgozd be a vetés előtt.',
            ]
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 2. PROTOKOLL: FRISS VETÉS / FELÜLVETÉS (KELÉSI IDŐSZAK: 0–21. NAP)
    # ─────────────────────────────────────────────────────────────────────────
    if stage == 'Friss vetés / Felülvetés':
        days_since_seed = None
        if lawn.seeding_date:
            days_since_seed = (today - lawn.seeding_date).days

        if days_since_seed is not None and days_since_seed > 25:
            seed_phase_text = f"A vetés óta {days_since_seed} nap telt el – Megerősödési fázis"
            frequency_label = "Napi 1-2 alkalommal (átmenet a mély öntözésre)"
            l_per_sqm = "8 – 12"
            per_day_times = "Napi 1-2x"
        elif days_since_seed is not None:
            seed_phase_text = f"Kelési fázis: {days_since_seed}. nap / 21 napos csíráztatás"
            frequency_label = "Naponta 3–5 alkalommal finom permetezéssel"
            l_per_sqm = "2 – 3 (alkalmanként)"
            per_day_times = "Napi 3-5x"
        else:
            seed_phase_text = "Friss vetési csíráztatási időszak"
            frequency_label = "Naponta 3–5 alkalommal finom permetezéssel"
            l_per_sqm = "2 – 3 (alkalmanként)"
            per_day_times = "Napi 3-5x"

        daily_l = int(round(area * 10.0))
        reasons = [
            '🚨 Életmentő csíráztatási szabály: A csírázó fűmag nem száradhat ki egyetlen órára sem! Ha a csíra megszárad a napon, menthetetlenül elpusztul.',
            '💧 Rövid mikrociklusok: Napi 3–5 alkalommal, 5–8 perces finom permetező öntözés szükséges (főleg 10:00, 13:00, 16:00 órakor), hogy a talaj felső 1–2 cm-e folyamatosan nyirkos maradjon.',
            '⛔ Kerüld a tócsásodást és a nagynyomású sugarat: A lezúduló víz elmoshatja a laza fűmagot!',
            '✂️ Fűnyírás még szigorúan tilos: Várd meg, amíg a fű eléri a 7–8 cm-es magasságot, és a gyökérzet stabilizálódik.',
        ]

        if weather and weather.get('temp', 20) >= 28:
            reasons.append(f'🔥 Kánikula ({weather["temp"]:.1f}°C): A felső talajréteg perceken belül kiszárad, iktass be extra délutáni hűsítő permetezést!')

        return {
            'stage': 'fresh_seed',
            'stage_badge': f'🌿 Friss Vetési Protokoll ({seed_phase_text})',
            'interval_days': 1,
            'frequency_label': frequency_label,
            'water_amount_l_per_sqm': l_per_sqm,
            'total_liters': daily_l,
            'total_m3': round(daily_l / 1000.0, 1),
            'recommended_time': 'Napközben elosztva (08:00, 11:00, 14:00, 17:00)',
            'days_since_water': None,
            'due_in': 0,
            'status': 'fresh_seed_active',
            'status_label': f'Folyamatos nedvesen tartás ({per_day_times})',
            'status_color': 'warning',
            'fertilizer_flush_required': False,
            'weather_warning': None,
            'reasoning': reasons,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 3. PROTOKOLL: MEGLÉVŐ, BEÁLLT GYEP (MÉLY ÖNTÖZÉSI MODELL)
    # ─────────────────────────────────────────────────────────────────────────
    if season == 'winter':
        return {
            'stage': 'established',
            'stage_badge': '🏡 Meglévő, beállt gyep',
            'interval_days': 20,
            'frequency_label': 'Téli nyugalmi időszak (öntözés szünetel)',
            'water_amount_l_per_sqm': '0',
            'total_liters': 0,
            'total_m3': 0,
            'recommended_time': 'Nincs szükség öntözésre',
            'days_since_water': days_since(lawn.last_watering().date) if lawn.last_watering() else None,
            'due_in': 999,
            'status': 'dormant',
            'status_label': 'Téli pihenő',
            'status_color': 'gray',
            'fertilizer_flush_required': False,
            'weather_warning': None,
            'reasoning': ['Télen a fagyveszély és a nyugalmi állapot miatt a gyep nem igényel mesterséges öntözést.'],
        }

    # 1. Bázis intervallum & vízmennyiség évszakonként
    base_intervals = {
        'spring': 5.0,
        'summer': 3.5,
        'autumn': 6.0,
    }
    base_liters_per_sqm = {
        'spring': 15.0,
        'summer': 20.0,
        'autumn': 15.0,
    }

    interval = base_intervals.get(season, 4.0)
    liters_per_sqm = base_liters_per_sqm.get(season, 18.0)
    reasons = []

    # 2. Talajtípus hatása
    soil = lawn.soil_type or 'Vályogos'
    if soil == 'Homokos':
        interval -= 1.0
        liters_per_sqm -= 3.0
        reasons.append('🏖️ Homokos talaj: Alacsony vízkapacitás, a víz gyorsan átszivárog. Kisebb adagok (12–15 l/m²), de sűrűbb öntözés szükséges.')
    elif soil == 'Agyagos':
        interval += 1.5
        liters_per_sqm += 3.0
        reasons.append('🏺 Agyagos talaj: Nagy vízmegtartó képesség, de lassú beszivárgás. Ritkább, mély öntözés (20–25 l/m²), ciklikus adagolással a tócsásodás elkerülésére.')
    elif soil in ['Vályogos', 'Tőzeges']:
        reasons.append(f'🌱 {soil} talaj: Ideális víz-levegő arány. Kiegyensúlyozott 15–20 l/m² mély öntözés.')

    # 3. Napkitettség hatása
    sun = lawn.sun_exposure or 'Teljes nap'
    if sun == 'Árnyékos':
        interval += 2.0
        liters_per_sqm *= 0.7
        reasons.append('🌳 Árnyékos terület: Jelentősen alacsonyabb párolgás. Ritkább öntözés szükséges a mohásodás és gombásodás megelőzésére.')
    elif sun == 'Félárnyas':
        interval += 0.5
        liters_per_sqm *= 0.85
        reasons.append('⛅ Félárnyas terület: Mérsékelt párolgási veszteség (-15% vízigény).')
    else:
        reasons.append('☀️ Teljes napsütés: Maximális evaporáció, a teljes napi vízveszteség pótlása szükséges.')

    # 4. Fűmag / Fűtípus fajtajellemzők
    grass_str = f"{lawn.grass_type or ''} {lawn.seed_product.product_name if lawn.seed_product else ''} {lawn.seed_product.grass_types if lawn.seed_product else ''}".lower()
    if any(k in grass_str for k in ['nádképű', 'water saver', 'trockenrasen', 'mediterran']):
        interval += 1.0
        liters_per_sqm += 2.0
        reasons.append('🌾 Nádképű csenkesz (Szárazságtűrő): 50–80 cm mélyre hatoló gyökérzet. Nagyon jól bírja a ritka, de alapos mély öntözést.')
    elif any(k in grass_str for k in ['angol perje', 'sport', 'rpr', 'gyors']):
        interval -= 0.5
        reasons.append('⚽ Angol perje / Sportkeverék: Sekélyebb gyökérzóna (10–15 cm), rendszeresebb vízutánpótlást igényel.')

    # 5. Időjárási tényezők
    weather_warning = None
    if weather:
        temp = weather.get('temp', 22)
        rain_1h = weather.get('rain_1h', 0)
        wind_speed = weather.get('wind_speed', 10)

        if rain_1h > 0:
            weather_warning = '🌧️ Jelenleg esik az eső – a természetes csapadék miatt az öntözés elhalasztható!'
            reasons.append('🌧️ Aktuális csapadék: Esős időben az öntözés leállítása szükséges a felesleges víz és gombásodás elkerülésére.')

        if temp >= 30:
            interval -= 1.0
            liters_per_sqm += 4.0
            reasons.append(f'🔥 Nyári hőség ({temp:.1f}°C): A napi párolgási veszteség eléri a 6–8 mm-t (l/m²). Növelt vízmennyiség szükséges.')
        elif temp <= 16:
            interval += 1.5
            liters_per_sqm -= 3.0
            reasons.append(f'🌡️ Hűvös időjárás ({temp:.1f}°C): Alacsony párolgás, ritkább öntözési igény.')

        if wind_speed > 25:
            reasons.append(f'💨 Erős szél ({wind_speed} km/h): Szórófejes öntözésnél a szél elfújja a vízsugarat, egyenetlen öntözést okozva.')

    # 6. Friss trágyázási bemosási riasztás
    last_fert = lawn.last_fertilizing()
    fert_flush = False
    if last_fert and last_fert.date:
        fert_days = (today - last_fert.date).days
        last_wat = lawn.last_watering()
        wat_after_fert = last_wat and last_wat.date and last_wat.date >= last_fert.date
        if fert_days <= 2 and not wat_after_fert:
            fert_flush = True
            reasons.insert(0, '🚨 SÜRGŐS BEMOSÓ ÖNTÖZÉS SZÜKSÉGES: Friss műtrágyázás történt! Azonnali 10–15 l/m² öntözés kötelező a műtrágyaszemcsék bemosásához és a gyep kiégésének megelőzéséhez!')

    # Számítások összesítése
    final_interval = max(2, min(8, int(round(interval))))
    final_liters_sqm = max(10, min(25, int(round(liters_per_sqm))))
    total_liters = int(round(area * final_liters_sqm))
    total_m3 = round(total_liters / 1000.0, 1)

    if final_interval <= 2:
        frequency_label = 'Hetente 3-4 alkalommal (2 naponta)'
    elif final_interval <= 3:
        frequency_label = 'Hetente 2-3 alkalommal (3 naponta)'
    elif final_interval <= 4:
        frequency_label = 'Hetente 2 alkalommal (3–4 naponta)'
    elif final_interval <= 6:
        frequency_label = 'Hetente 1-2 alkalommal (5–6 naponta)'
    else:
        frequency_label = f'{final_interval} naponta egyszer'

    # Esedékesség
    last_water = lawn.last_watering()
    if last_water and last_water.date:
        days_since_water = (today - last_water.date).days
        due_in = final_interval - days_since_water
    else:
        days_since_water = 999
        due_in = -999

    if fert_flush:
        status = 'fertilizer_flush'
        status_label = '🚨 Azonnali bemosó öntözés szükséges!'
        status_color = 'danger'
    elif weather and weather.get('rain_1h', 0) > 0:
        status = 'rain_skip'
        status_label = '🌧️ Eső miatt kihagyható'
        status_color = 'info'
    elif days_since_water == 999:
        status = 'no_data'
        status_label = 'Még nincs öntözési adat'
        status_color = 'gray'
    elif due_in < -2:
        status = 'severely_overdue'
        status_label = f'Sürgős: {days_since_water} napja nem volt öntözés!'
        status_color = 'danger'
    elif due_in < 0:
        status = 'overdue'
        status_label = f'Esedékes ({-due_in} napja esedékes)'
        status_color = 'danger'
    elif due_in == 0:
        status = 'due_today'
        status_label = 'Ma hajnalban esedékes!'
        status_color = 'warning'
    elif due_in <= 1:
        status = 'due_soon'
        status_label = 'Holnap hajnalban esedékes'
        status_color = 'info'
    else:
        status = 'ok'
        status_label = f'Rendben ({due_in} nap múlva esedékes)'
        status_color = 'success'

    reasons.append('⏰ Ideális időpont: Hajnalban (05:00 – 07:00). Minimális párolgási veszteség, a levélzet gyorsan felszárad napkeltekor, megelőzve a gombás fertőzéseket (pl. Dollárfolt, Rozsda).')

    return {
        'stage': 'established',
        'stage_badge': '🏡 Meglévő, beállt gyep (Mély öntözési modell)',
        'interval_days': final_interval,
        'frequency_label': frequency_label,
        'water_amount_l_per_sqm': str(final_liters_sqm),
        'total_liters': total_liters,
        'total_m3': total_m3,
        'recommended_time': 'Hajnalban (05:00 – 07:00)',
        'days_since_water': days_since_water if days_since_water != 999 else None,
        'due_in': due_in if days_since_water != 999 else None,
        'status': status,
        'status_label': status_label,
        'status_color': status_color,
        'fertilizer_flush_required': fert_flush,
        'weather_warning': weather_warning,
        'reasoning': reasons,
    }


def generate_suggestions(lawn, weather=None):
    """
    Generál javaslatokat egy gyep profil alapján.
    Visszaad egy listát dict-ekből: {title, message, priority, icon, action}
    """
    suggestions = []
    today = date.today()
    season = get_season()
    month = today.month

    # --- INTELLIGENS ÖNTÖZÉS JAVASLATOK ---
    wat_plan = calculate_watering_plan(lawn, weather)
    if wat_plan['stage'] == 'fresh_seed':
        suggestions.append({
            'icon': '🌱',
            'title': 'Friss Vetés: Folyamatos párásító öntözés',
            'message': f"A fűmag csírázik! Öntözz naponta 3–5 alkalommal finoman permetezve ({wat_plan['water_amount_l_per_sqm']} l/m²). A magágy nem száradhat ki!",
            'priority': 'high',
            'action': 'watering',
        })
    elif wat_plan['stage'] == 'before_seed':
        suggestions.append({
            'icon': '🚜',
            'title': 'Vetés előtt: Magágy előáztatás',
            'message': f"Vetés előtt 1-2 nappal alaposan áztasd be a talajt ({wat_plan['water_amount_l_per_sqm']} l/m², összesen ~{wat_plan['total_liters']} liter).",
            'priority': 'medium',
            'action': 'watering',
        })
    elif season != 'winter':
        if wat_plan['fertilizer_flush_required']:
            suggestions.append({
                'icon': '🚨',
                'title': 'SÜRGŐS: Műtrágya bemosó öntözés!',
                'message': 'Friss műtrágyázás történt! Azonnal öntözd be a gyepet 10–15 l/m² vízzel, hogy elkerüld a perzselést és aktiváld a tápanyagot.',
                'priority': 'high',
                'action': 'watering',
            })
        elif wat_plan['weather_warning']:
            suggestions.append({
                'icon': '🌧️',
                'title': 'Öntözés kihagyható',
                'message': wat_plan['weather_warning'],
                'priority': 'low',
                'action': None,
            })
        elif wat_plan['status'] in ('severely_overdue', 'overdue'):
            suggestions.append({
                'icon': '💧',
                'title': 'Sürgős: Öntözés szükséges!',
                'message': f"{wat_plan['days_since_water']} napja nem volt öntözés. Javasolt mennyiség: {wat_plan['water_amount_l_per_sqm']} l/m² "
                           f"({wat_plan['total_liters']} liter / {wat_plan['total_m3']} m³). Öntözz hajnalban!",
                'priority': 'high',
                'action': 'watering',
            })
        elif wat_plan['status'] == 'due_today':
            suggestions.append({
                'icon': '💧',
                'title': 'Öntözés ma esedékes',
                'message': f"Javasolt: {wat_plan['water_amount_l_per_sqm']} l/m² (összesen {wat_plan['total_liters']} liter). Ideális időpont: {wat_plan['recommended_time']}.",
                'priority': 'medium',
                'action': 'watering',
            })
        elif wat_plan['status'] == 'due_soon':
            suggestions.append({
                'icon': '💧',
                'title': 'Öntözés közeledik',
                'message': f"Holnap hajnalban esedékes az öntözés ({wat_plan['water_amount_l_per_sqm']} l/m²).",
                'priority': 'low',
                'action': 'watering',
            })

    # --- INTELLIGENS FŰNYÍRÁS JAVASLATOK ---
    mow_plan = calculate_mowing_plan(lawn, weather)
    if mow_plan.get('stage') == 'before_seed':
        pass  # Vetés előtt nincs nyírási javaslat
    elif mow_plan.get('status') == 'no_mow':
        suggestions.append({
            'icon': '🚫',
            'title': 'Friss Vetés: Fűnyírás szigorúan tilos!',
            'message': 'A csírázó fű gyökérzete még gyenge. A fűnyíró kitépné a szálakat, a kerekek megtömörítenék a magágyat. Várd meg a 7–8 cm-es magasságot!',
            'priority': 'medium',
            'action': None,
        })
    elif mow_plan.get('status') == 'first_cut':
        suggestions.append({
            'icon': '✂️',
            'title': 'Első kímélő fűnyírás esedékes',
            'message': 'A gyep elérte a megfelelő kort! Kizárólag borotvaéles késsel, csak a felső 1/3-ot levágva (5.5–6.5 cm) végezd el az első kímélő nyírást.',
            'priority': 'high',
            'action': 'mowing',
        })
    elif season != 'winter':
        if mow_plan['weather_warning']:
            suggestions.append({
                'icon': '🌧️',
                'title': 'Fűnyírás: Várj a felszáradásig!',
                'message': mow_plan['weather_warning'],
                'priority': 'medium',
                'action': None,
            })

        if mow_plan['status'] in ('severely_overdue', 'overdue'):
            msg = f"{mow_plan['days_since_mow']} napja nem volt nyírás (javasolt ciklus: {mow_plan['interval_days']} naponta). " \
                  f"Optimális vágási magasság: {mow_plan['recommended_height_cm']} cm. "
            if mow_plan['fertilizer_impact'] and mow_plan['fertilizer_impact']['level'] == 'surge':
                msg += "⚠️ Figyelem: A trágyázás miatti csúcsnövekedés miatt ne vágj le többet a szál 1/3-ánál!"
            suggestions.append({
                'icon': '✂️',
                'title': 'Sürgős: Fűnyírás szükséges!',
                'message': msg,
                'priority': 'high',
                'action': 'mowing',
            })
        elif mow_plan['status'] == 'due_today':
            suggestions.append({
                'icon': '✂️',
                'title': 'Fűnyírás ma esedékes',
                'message': f"A javasolt {mow_plan['frequency_label']} szerint ma ideális a nyírás. Vágási magasság: {mow_plan['recommended_height_cm']} cm.",
                'priority': 'medium',
                'action': 'mowing',
            })
        elif mow_plan['status'] == 'due_soon':
            suggestions.append({
                'icon': '✂️',
                'title': f"Fűnyírás {mow_plan['due_in']} nap múlva esedékes",
                'message': f"Javasolt ütem: {mow_plan['frequency_label']}. Ajánlott vágási magasság: {mow_plan['recommended_height_cm']} cm.",
                'priority': 'low',
                'action': 'mowing',
            })

    # --- TRÁGYÁZÁS ---
    last_fert = lawn.last_fertilizing()
    if last_fert and last_fert.date:
        fert_days = (today - last_fert.date).days
    else:
        fert_days = 999

    fert_interval = INTERVALS['fertilizing'].get(season, 90)

    if season == 'winter':
        pass
    elif fert_days >= INTERVALS['fertilizing']['warning']:
        fert_type_msg = season_fertilizer(season)
        suggestions.append({
            'icon': '🌱',
            'title': 'Trágyázás szükséges',
            'message': f'{fert_days} napja nem volt trágyázás. '
                       f'{fert_type_msg} '
                       f'Javasolt mennyiség: 30–40 g/m² ({lawn.area_sqm} m²-re: '
                       f'{30 * lawn.area_sqm:.0f}–{40 * lawn.area_sqm:.0f} g).',
            'priority': 'medium',
            'action': 'fertilizing',
        })
    elif fert_days >= fert_interval:
        fert_type_msg = season_fertilizer(season)
        suggestions.append({
            'icon': '🌱',
            'title': 'Trágyázás közeledik',
            'message': f'Hamarosan érdemes trágyázni. {fert_type_msg}',
            'priority': 'low',
            'action': 'fertilizing',
        })

    # --- SZELLŐZTETÉS ---
    last_aer = lawn.last_aeration()
    if last_aer and last_aer.date:
        aer_days = (today - last_aer.date).days
    else:
        aer_days = 999

    # Tavaszi szellőztetés: március–április
    if month in (3, 4) and aer_days > 180:
        suggestions.append({
            'icon': '🌬️',
            'title': 'Tavaszi szellőztetés',
            'message': 'Március–április az ideális idő a tavaszi gyepszellőztetésre. '
                       'Lazítja a talajt, eltávolítja a filcréteget.',
            'priority': 'medium',
            'action': 'aeration',
        })
    # Őszi szellőztetés: szeptember–október
    elif month in (9, 10) and aer_days > 180:
        suggestions.append({
            'icon': '🌬️',
            'title': 'Őszi szellőztetés',
            'message': 'Szeptember–október az őszi szellőztetés ideje. '
                       'Segíti a téliesítést és a gyökerek megerősödését.',
            'priority': 'medium',
            'action': 'aeration',
        })

    # --- SZEZONÁLIS TANÁCSOK ---
    seasonal = get_seasonal_tips(season, month, lawn)
    suggestions.extend(seasonal)

    return suggestions


def season_height(season):
    """Javasolt vágási magasság évszak szerint."""
    return {'spring': '4–5', 'summer': '5–6', 'autumn': '4–5', 'winter': '4–5'}.get(season, '4–5')


def season_fertilizer(season):
    """Javasolt műtrágya típus évszak szerint."""
    msgs = {
        'spring': 'Tavasszal nitrogéndús trágyát javaslunk (pl. ICL All Round 24-5-8).',
        'summer': 'Nyáron káliumdús vagy kiegyensúlyozott NPK trágyát javaslunk '
                  'a stressztűrés fokozásához (pl. ICL Stress Control 16-5-22).',
        'autumn': 'Ősszel káliumdús trágyát javaslunk (pl. ICL Stress Control 16-5-22 vagy Compo Herbst 4-5-20) '
                  'a téli felkészüléshez.',
    }
    return msgs.get(season, 'Komplex NPK trágyát javaslunk.')


def get_seasonal_tips(season, month, lawn):
    """Általános szezonális tanácsok."""
    tips = []

    if season == 'spring' and month == 3:
        tips.append({
            'icon': '🌸',
            'title': 'Tavaszi gyepindítás',
            'message': 'Március a gyep "ébredésének" ideje! Érdemes elvégezni az első '
                       'szellőztetést, nitrogéndús tavaszi trágyázást, és ha szükséges, '
                       'a kopasz foltok felülvetését.',
            'priority': 'low',
            'action': None,
        })

    if season == 'summer' and month in (7, 8):
        tips.append({
            'icon': '☀️',
            'title': 'Nyári hőség – figyeld a gyepet!',
            'message': 'Forró nyáron hagyd a füvet magasabbra (5–6 cm) – '
                       'így árnyékolja a talajt és csökkenti a párologtatást. '
                       'Öntözz inkább ritkábban, de mélyebben.',
            'priority': 'low',
            'action': None,
        })

    if season == 'autumn' and month == 9:
        tips.append({
            'icon': '🍂',
            'title': 'Őszi felkészítés ideje',
            'message': 'Szeptember: szellőztetés, őszi trágyázás, levelek eltávolítása. '
                       'Az őszi felkészítés kulcsfontosságú a tél túléléséhez.',
            'priority': 'low',
            'action': None,
        })

    if season == 'winter':
        tips.append({
            'icon': '❄️',
            'title': 'Téli pihenő',
            'message': 'Télen kerüld a gyep taposását, különösen fagyott állapotban. '
                       'A nyírást és trágyázást tavaszig halaszd.',
            'priority': 'low',
            'action': None,
        })

    return tips
