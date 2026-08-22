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


def generate_suggestions(lawn, weather=None):
    """
    Generál javaslatokat egy gyep profil alapján.
    Visszaad egy listát dict-ekből: {title, message, priority, icon, action}
    """
    suggestions = []
    today = date.today()
    season = get_season()
    month = today.month

    # --- ÖNTÖZÉS ---
    last_watering = lawn.last_watering()
    if last_watering and last_watering.date:
        days = (today - last_watering.date).days
    else:
        days = 999

    # Időjárás-alapú módosítás: ha esett nemrég, csökkentjük az igényt
    rain_recently = False
    if weather and weather.get('rain_1h', 0) > 0:
        rain_recently = True

    watering_interval = INTERVALS['watering'].get(lawn.soil_type,
                                                   INTERVALS['watering']['default'])
    if season == 'summer':
        watering_interval = INTERVALS['watering']['summer']
    elif season in ('autumn', 'winter'):
        watering_interval = INTERVALS['watering']['default'] + 3

    if not rain_recently:
        if days >= INTERVALS['watering']['warning']:
            suggestions.append({
                'icon': '💧',
                'title': 'Sürgős: Öntözés szükséges!',
                'message': f'{days} napja nem volt öntözés – a gyep kiszáradhat. '
                           f'Öntözd meg most, lehetőleg hajnalban vagy este. '
                           f'Javasolt: {2 * lawn.area_sqm:.0f}–{2.5 * lawn.area_sqm:.0f} liter.',
                'priority': 'high',
                'action': 'watering',
            })
        elif days >= watering_interval:
            suggestions.append({
                'icon': '💧',
                'title': 'Öntözés javasolt',
                'message': f'Utolsó öntözés {days} napja volt. '
                           f'Javasolt mennyiség: ~{2 * lawn.area_sqm:.0f} liter '
                           f'({lawn.area_sqm} m²-re).',
                'priority': 'medium',
                'action': 'watering',
            })
    else:
        suggestions.append({
            'icon': '🌧️',
            'title': 'Öntözés kihagyható',
            'message': 'Jelenleg esik az eső – az öntözés nem szükséges.',
            'priority': 'low',
            'action': None,
        })

    # --- FŰNYÍRÁS ---
    last_mowing = lawn.last_mowing()
    if last_mowing and last_mowing.date:
        mow_days = (today - last_mowing.date).days
    else:
        mow_days = 999

    mow_interval = INTERVALS['mowing'].get(season, INTERVALS['mowing']['summer'])

    if season == 'winter':
        pass  # Télen nem kell nyírás
    elif mow_days >= INTERVALS['mowing']['warning']:
        suggestions.append({
            'icon': '✂️',
            'title': 'Sürgős: Fűnyírás szükséges!',
            'message': f'{mow_days} napja nem volt nyírás. A fű valószínűleg '
                       f'már nagyon megnyőtt. Javasolt vágási magasság {season_height(season)} cm.',
            'priority': 'high',
            'action': 'mowing',
        })
    elif mow_days >= mow_interval:
        suggestions.append({
            'icon': '✂️',
            'title': 'Fűnyírás javasolt',
            'message': f'Utolsó nyírás {mow_days} napja volt. '
                       f'Javasolt vágási magasság: {season_height(season)} cm.',
            'priority': 'medium',
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
