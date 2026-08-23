"""
app.py – GyepMester Flask alkalmazás főfájlja.
"""
import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

from config import Config
from models import (db, User, LawnProfile, GrassSeedProduct, FertilizerProduct,
                    WateringLog, MowingLog, FertilizingLog, AerationLog, WeedLog, PestLog)
from seed_data import seed_products
from utils.suggestions import generate_suggestions, calculate_mowing_plan, calculate_watering_plan
from utils.weather import get_weather
from utils.helpers import save_photo, delete_photo, days_since

# =============================================================================
# APP INICIALIZÁCIÓ
# =============================================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Kérjük, jelentkezz be az oldal megtekintéséhez.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Jinja2 segédfüggvények
app.jinja_env.globals['days_since'] = days_since
app.jinja_env.globals['now'] = datetime.now
app.jinja_env.globals['calculate_mowing_plan'] = calculate_mowing_plan
app.jinja_env.globals['calculate_watering_plan'] = calculate_watering_plan


# =============================================================================
# AUTENTIKÁCIÓ
# =============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('A felhasználónév legalább 3 karakter legyen.')
        if User.query.filter_by(username=username).first():
            errors.append('Ez a felhasználónév már foglalt.')
        if not email or '@' not in email:
            errors.append('Érvényes e-mail cím szükséges.')
        if User.query.filter_by(email=email).first():
            errors.append('Ez az e-mail cím már regisztrálva van.')
        if len(password) < 6:
            errors.append('A jelszó legalább 6 karakter legyen.')
        if password != password2:
            errors.append('A két jelszó nem egyezik.')

        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Üdvözlünk, {username}! A fiókod sikeresen létrejött.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Szia, {user.username}! Sikeresen bejelentkeztél.', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Hibás felhasználónév vagy jelszó.', 'danger')

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sikeresen kijelentkeztél.', 'info')
    return redirect(url_for('login'))


# =============================================================================
# DASHBOARD (FŐOLDAL)
# =============================================================================

@app.route('/')
@login_required
def dashboard():
    lawns = current_user.lawn_profiles.all()
    weather_data = None

    # Időjárás lekérés az első gyep helyszíne alapján
    if lawns and app.config.get('OPENWEATHER_API_KEY'):
        weather_data = get_weather(lawns[0].location_city, app.config['OPENWEATHER_API_KEY'])

    # Javaslatok generálása
    suggestions = []
    for lawn in lawns:
        suggestions.extend(generate_suggestions(lawn, weather_data))

    # Sürgős javaslatok kiemelése
    urgent = [s for s in suggestions if s['priority'] == 'high'][:3]
    normal = [s for s in suggestions if s['priority'] != 'high'][:5]

    return render_template('dashboard.html',
                           lawns=lawns,
                           weather=weather_data,
                           urgent_suggestions=urgent,
                           suggestions=normal)


# =============================================================================
# GYEP PROFILOK
# =============================================================================

@app.route('/profiles')
@login_required
def profiles():
    lawns = current_user.lawn_profiles.order_by(LawnProfile.created_at.desc()).all()
    return render_template('profile/list.html', lawns=lawns)


@app.route('/profiles/new', methods=['GET', 'POST'])
@login_required
def new_profile():
    grass_products = GrassSeedProduct.query.order_by(GrassSeedProduct.brand).all()
    # Márkánként csoportosítva
    brands = {}
    for p in grass_products:
        brands.setdefault(p.brand, []).append(p)

    fertilizer_products = FertilizerProduct.query.order_by(FertilizerProduct.brand).all()
    fertilizer_brands = {}
    for p in fertilizer_products:
        fertilizer_brands.setdefault(p.brand, []).append(p)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        area_sqm = request.form.get('area_sqm', '').strip()
        location_city = request.form.get('location_city', '').strip()
        soil_type = request.form.get('soil_type', '')
        sun_exposure = request.form.get('sun_exposure', '')
        grass_source = request.form.get('grass_type_source', 'manual')
        grass_product_id = request.form.get('grass_seed_product_id') or None
        grass_type = request.form.get('grass_type', '').strip()
        cultivation_method = request.form.get('cultivation_method', '')
        mowing_method = request.form.get('mowing_method', '')
        lawn_stage = request.form.get('lawn_stage', 'Meglévő, beállt gyep')

        # Vetés dátuma
        seeding_date_str = request.form.get('seeding_date', '').strip()
        seeding_date = None
        if seeding_date_str and lawn_stage == 'Friss vetés / Felülvetés':
            try:
                seeding_date = datetime.strptime(seeding_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Fűnyírókés élezési dátum
        blade_date_str = request.form.get('blade_sharpened_at', '').strip()
        blade_sharpened_at = None
        if blade_date_str:
            try:
                blade_sharpened_at = datetime.strptime(blade_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        errors = []
        if not name:
            errors.append('A gyep neve kötelező.')
        if not area_sqm or not area_sqm.replace('.', '', 1).isdigit():
            errors.append('Érvényes terület szükséges (pl. 150.5).')
        if not location_city:
            errors.append('A helyszín (város) kötelező.')

        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            # Termékből auto-kitöltés
            if grass_source == 'product' and grass_product_id:
                product = GrassSeedProduct.query.get(int(grass_product_id))
                if product:
                    grass_type = product.grass_types

            # Fotó feltöltés
            photo_filename = None
            if 'photo' in request.files:
                photo_filename = save_photo(request.files['photo'],
                                            app.config['UPLOAD_FOLDER'],
                                            app.config['ALLOWED_EXTENSIONS'])

            lawn = LawnProfile(
                user_id=current_user.id,
                name=name,
                area_sqm=float(area_sqm),
                location_city=location_city,
                soil_type=soil_type,
                sun_exposure=sun_exposure,
                grass_type=grass_type,
                grass_type_source=grass_source,
                grass_seed_product_id=int(grass_product_id) if grass_product_id else None,
                photo=photo_filename,
                cultivation_method=cultivation_method or None,
                mowing_method=mowing_method or None,
                lawn_stage=lawn_stage or 'Meglévő, beállt gyep',
                seeding_date=seeding_date,
                blade_sharpened_at=blade_sharpened_at,
            )
            db.session.add(lawn)
            db.session.flush()  # lawn.id elkérése commit előtt

            # Tápanyag előzmény – FertilizingLog létrehozása
            last_fert_date_str = request.form.get('last_fertilizing_date', '').strip()
            if last_fert_date_str:
                try:
                    last_fert_date = datetime.strptime(last_fert_date_str, '%Y-%m-%d').date()
                    init_fert_source = request.form.get('init_fertilizer_type_source', 'manual')
                    init_fert_product_id = request.form.get('init_fertilizer_product_id') or None
                    init_fert_type = request.form.get('init_fertilizer_type', '').strip()
                    init_npk_n = request.form.get('init_npk_n', type=float)
                    init_npk_p = request.form.get('init_npk_p', type=float)
                    init_npk_k = request.form.get('init_npk_k', type=float)

                    if init_fert_source == 'product' and init_fert_product_id:
                        fp = FertilizerProduct.query.get(int(init_fert_product_id))
                        if fp:
                            init_fert_type = fp.fertilizer_type
                            init_npk_n, init_npk_p, init_npk_k = fp.npk_n, fp.npk_p, fp.npk_k

                    fert_log = FertilizingLog(
                        lawn_id=lawn.id,
                        date=last_fert_date,
                        fertilizer_product_id=int(init_fert_product_id) if init_fert_product_id else None,
                        fertilizer_type=init_fert_type or None,
                        fertilizer_type_source=init_fert_source,
                        npk_n=init_npk_n,
                        npk_p=init_npk_p,
                        npk_k=init_npk_k,
                        notes='(Profil létrehozáskor rögzített előzmény)',
                    )
                    db.session.add(fert_log)
                except ValueError:
                    pass  # Hibás dátum esetén kihagyjuk

            db.session.commit()
            flash(f'"{name}" gyep profil sikeresen létrehozva!', 'success')
            return redirect(url_for('profiles'))

    return render_template('profile/new.html', brands=brands, fertilizer_brands=fertilizer_brands)


@app.route('/profiles/<int:lawn_id>')
@login_required
def profile_detail(lawn_id):
    lawn = LawnProfile.query.get_or_404(lawn_id)
    if lawn.user_id != current_user.id:
        abort(403)
    
    weather_data = None
    if app.config.get('OPENWEATHER_API_KEY'):
        weather_data = get_weather(lawn.location_city, app.config['OPENWEATHER_API_KEY'])

    mowing_plan = calculate_mowing_plan(lawn, weather_data)
    watering_plan = calculate_watering_plan(lawn, weather_data)
    suggestions = generate_suggestions(lawn, weather_data)
    recent_waterings = lawn.watering_logs.order_by(WateringLog.date.desc()).limit(5).all()
    
    return render_template('profile/detail.html', lawn=lawn, suggestions=suggestions,
                           recent_waterings=recent_waterings,
                           mowing_plan=mowing_plan, watering_plan=watering_plan,
                           weather=weather_data)


@app.route('/profiles/<int:lawn_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(lawn_id):
    lawn = LawnProfile.query.get_or_404(lawn_id)
    if lawn.user_id != current_user.id:
        abort(403)

    grass_products = GrassSeedProduct.query.order_by(GrassSeedProduct.brand).all()
    brands = {}
    for p in grass_products:
        brands.setdefault(p.brand, []).append(p)

    fertilizer_products = FertilizerProduct.query.order_by(FertilizerProduct.brand).all()
    fertilizer_brands = {}
    for p in fertilizer_products:
        fertilizer_brands.setdefault(p.brand, []).append(p)

    if request.method == 'POST':
        lawn.name = request.form.get('name', '').strip()
        area = request.form.get('area_sqm', '').strip()
        if area and area.replace('.', '', 1).isdigit():
            lawn.area_sqm = float(area)
        lawn.location_city = request.form.get('location_city', '').strip()
        lawn.soil_type = request.form.get('soil_type', '')
        lawn.sun_exposure = request.form.get('sun_exposure', '')
        grass_source = request.form.get('grass_type_source', 'manual')
        grass_product_id = request.form.get('grass_seed_product_id') or None
        grass_type = request.form.get('grass_type', '').strip()
        lawn.cultivation_method = request.form.get('cultivation_method', '') or None
        lawn.mowing_method = request.form.get('mowing_method', '') or None
        lawn.lawn_stage = request.form.get('lawn_stage', 'Meglévő, beállt gyep')

        # Vetés dátuma
        seeding_date_str = request.form.get('seeding_date', '').strip()
        if seeding_date_str and lawn.lawn_stage == 'Friss vetés / Felülvetés':
            try:
                lawn.seeding_date = datetime.strptime(seeding_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            lawn.seeding_date = None

        # Fűnyírókés élezési dátum
        blade_date_str = request.form.get('blade_sharpened_at', '').strip()
        if blade_date_str:
            try:
                lawn.blade_sharpened_at = datetime.strptime(blade_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            lawn.blade_sharpened_at = None

        if grass_source == 'product' and grass_product_id:
            product = GrassSeedProduct.query.get(int(grass_product_id))
            if product:
                grass_type = product.grass_types

        lawn.grass_type = grass_type
        lawn.grass_type_source = grass_source
        lawn.grass_seed_product_id = int(grass_product_id) if grass_product_id else None

        if 'photo' in request.files and request.files['photo'].filename:
            if lawn.photo:
                delete_photo(lawn.photo, app.config['UPLOAD_FOLDER'])
            lawn.photo = save_photo(request.files['photo'],
                                    app.config['UPLOAD_FOLDER'],
                                    app.config['ALLOWED_EXTENSIONS'])

        # Tápanyag előzmény – FertilizingLog hozzáadása szerkesztéskor
        last_fert_date_str = request.form.get('last_fertilizing_date', '').strip()
        if last_fert_date_str:
            try:
                last_fert_date = datetime.strptime(last_fert_date_str, '%Y-%m-%d').date()
                init_fert_source = request.form.get('init_fertilizer_type_source', 'manual')
                init_fert_product_id = request.form.get('init_fertilizer_product_id') or None
                init_fert_type = request.form.get('init_fertilizer_type', '').strip()
                init_npk_n = request.form.get('init_npk_n', type=float)
                init_npk_p = request.form.get('init_npk_p', type=float)
                init_npk_k = request.form.get('init_npk_k', type=float)

                if init_fert_source == 'product' and init_fert_product_id:
                    fp = FertilizerProduct.query.get(int(init_fert_product_id))
                    if fp:
                        init_fert_type = fp.fertilizer_type
                        init_npk_n, init_npk_p, init_npk_k = fp.npk_n, fp.npk_p, fp.npk_k

                fert_log = FertilizingLog(
                    lawn_id=lawn.id,
                    date=last_fert_date,
                    fertilizer_product_id=int(init_fert_product_id) if init_fert_product_id else None,
                    fertilizer_type=init_fert_type or None,
                    fertilizer_type_source=init_fert_source,
                    npk_n=init_npk_n,
                    npk_p=init_npk_p,
                    npk_k=init_npk_k,
                    notes='(Profil szerkesztésekor rögzített előzmény)',
                )
                db.session.add(fert_log)
            except ValueError:
                pass

        db.session.commit()
        flash('A gyep profil sikeresen frissítve!', 'success')
        return redirect(url_for('profile_detail', lawn_id=lawn.id))

    return render_template('profile/edit.html', lawn=lawn, brands=brands,
                           fertilizer_brands=fertilizer_brands)


@app.route('/profiles/<int:lawn_id>/delete', methods=['POST'])
@login_required
def delete_profile(lawn_id):
    lawn = LawnProfile.query.get_or_404(lawn_id)
    if lawn.user_id != current_user.id:
        abort(403)
    name = lawn.name
    if lawn.photo:
        delete_photo(lawn.photo, app.config['UPLOAD_FOLDER'])
    db.session.delete(lawn)
    db.session.commit()
    flash(f'"{name}" gyep profil törölve.', 'info')
    return redirect(url_for('profiles'))


# =============================================================================
# TEVÉKENYSÉGEK (NAPLÓK)
# =============================================================================

@app.route('/activities')
@login_required
def activities():
    lawns = current_user.lawn_profiles.all()
    lawn_id = request.args.get('lawn_id', type=int)
    log_type = request.args.get('type', 'watering')

    # Alapértelmezés: első gyep
    selected_lawn = None
    if lawn_id:
        selected_lawn = LawnProfile.query.filter_by(id=lawn_id, user_id=current_user.id).first()
    if not selected_lawn and lawns:
        selected_lawn = lawns[0]

    logs = []
    if selected_lawn:
        if log_type == 'watering':
            logs = selected_lawn.watering_logs.order_by(WateringLog.date.desc()).all()
        elif log_type == 'mowing':
            logs = selected_lawn.mowing_logs.order_by(MowingLog.date.desc()).all()
        elif log_type == 'fertilizing':
            logs = selected_lawn.fertilizing_logs.order_by(FertilizingLog.date.desc()).all()
        elif log_type == 'aeration':
            logs = selected_lawn.aeration_logs.order_by(AerationLog.date.desc()).all()
        elif log_type == 'weed':
            logs = selected_lawn.weed_logs.order_by(WeedLog.date.desc()).all()
        elif log_type == 'pest':
            logs = selected_lawn.pest_logs.order_by(PestLog.date.desc()).all()

    return render_template('activities/list.html',
                           lawns=lawns,
                           selected_lawn=selected_lawn,
                           log_type=log_type,
                           logs=logs)


@app.route('/activities/add/<log_type>', methods=['GET', 'POST'])
@login_required
def add_activity(log_type):
    lawns = current_user.lawn_profiles.all()
    if not lawns:
        flash('Először hozz létre egy gyep profilt!', 'warning')
        return redirect(url_for('new_profile'))

    fertilizer_products = []
    fertilizer_brands = {}
    if log_type == 'fertilizing':
        fertilizer_products = FertilizerProduct.query.order_by(FertilizerProduct.brand).all()
        for p in fertilizer_products:
            fertilizer_brands.setdefault(p.brand, []).append(p)

    if request.method == 'POST':
        lawn_id = request.form.get('lawn_id', type=int)
        lawn = LawnProfile.query.filter_by(id=lawn_id, user_id=current_user.id).first()
        if not lawn:
            flash('Érvénytelen gyep.', 'danger')
            return redirect(url_for('activities'))

        log_date = request.form.get('date')
        if log_date:
            log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
        else:
            log_date = date.today()

        photo_filename = None
        if 'photo' in request.files and request.files['photo'].filename:
            photo_filename = save_photo(request.files['photo'],
                                        app.config['UPLOAD_FOLDER'],
                                        app.config['ALLOWED_EXTENSIONS'])

        notes = request.form.get('notes', '').strip()

        if log_type == 'watering':
            log = WateringLog(
                lawn_id=lawn.id,
                date=log_date,
                duration_min=request.form.get('duration_min', type=int),
                amount_liters=request.form.get('amount_liters', type=float),
                method=request.form.get('method', ''),
                photo=photo_filename,
                notes=notes,
            )

        elif log_type == 'mowing':
            log = MowingLog(
                lawn_id=lawn.id,
                date=log_date,
                height_cm=request.form.get('height_cm', type=float),
                condition_before=request.form.get('condition_before', ''),
                photo=photo_filename,
                notes=notes,
            )

        elif log_type == 'fertilizing':
            fert_source = request.form.get('fertilizer_type_source', 'manual')
            fert_product_id = request.form.get('fertilizer_product_id') or None
            fert_type = request.form.get('fertilizer_type', '').strip()
            npk_n = request.form.get('npk_n', type=float)
            npk_p = request.form.get('npk_p', type=float)
            npk_k = request.form.get('npk_k', type=float)

            if fert_source == 'product' and fert_product_id:
                fp = FertilizerProduct.query.get(int(fert_product_id))
                if fp:
                    fert_type = fp.fertilizer_type
                    npk_n, npk_p, npk_k = fp.npk_n, fp.npk_p, fp.npk_k

            log = FertilizingLog(
                lawn_id=lawn.id,
                date=log_date,
                fertilizer_product_id=int(fert_product_id) if fert_product_id else None,
                fertilizer_type=fert_type,
                fertilizer_type_source=fert_source,
                npk_n=npk_n,
                npk_p=npk_p,
                npk_k=npk_k,
                amount_per_sqm=request.form.get('amount_per_sqm', type=float),
                photo=photo_filename,
                notes=notes,
            )

        elif log_type == 'aeration':
            log = AerationLog(
                lawn_id=lawn.id,
                date=log_date,
                method=request.form.get('method', ''),
                overseeded=request.form.get('overseeded') == 'on',
                photo=photo_filename,
                notes=notes,
            )

        elif log_type == 'weed':
            log = WeedLog(
                lawn_id=lawn.id,
                date=log_date,
                method=request.form.get('method', ''),
                product_name=request.form.get('product_name', '').strip(),
                severity=request.form.get('severity', ''),
                photo=photo_filename,
                notes=notes,
            )

        elif log_type == 'pest':
            log = PestLog(
                lawn_id=lawn.id,
                date=log_date,
                pest_type=request.form.get('pest_type', ''),
                severity=request.form.get('severity', ''),
                treatment=request.form.get('treatment', '').strip(),
                photo=photo_filename,
                notes=notes,
            )
        else:
            flash('Ismeretlen tevékenység típus.', 'danger')
            return redirect(url_for('activities'))

        db.session.add(log)
        db.session.commit()
        flash('Tevékenység sikeresen rögzítve!', 'success')
        return redirect(url_for('activities', lawn_id=lawn.id, type=log_type))

    # Előre kiválasztott gyep (query param alapján)
    preselected_lawn_id = request.args.get('lawn_id', type=int)

    return render_template('activities/add.html',
                           log_type=log_type,
                           lawns=lawns,
                           preselected_lawn_id=preselected_lawn_id,
                           fertilizer_brands=fertilizer_brands,
                           today=date.today().isoformat())


# =============================================================================
# JAVASLATOK
# =============================================================================

@app.route('/suggestions')
@login_required
def suggestions():
    lawns = current_user.lawn_profiles.all()
    weather_data = None

    if lawns and app.config.get('OPENWEATHER_API_KEY'):
        weather_data = get_weather(lawns[0].location_city, app.config['OPENWEATHER_API_KEY'])

    all_suggestions = []
    for lawn in lawns:
        lawn_suggestions = generate_suggestions(lawn, weather_data)
        for s in lawn_suggestions:
            s['lawn_name'] = lawn.name
            s['lawn_id'] = lawn.id
        all_suggestions.extend(lawn_suggestions)

    # Prioritás szerint rendezve
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    all_suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))

    return render_template('suggestions.html',
                           suggestions=all_suggestions,
                           weather=weather_data,
                           lawns=lawns)


# =============================================================================
# NAPTÁR
# =============================================================================

@app.route('/calendar')
@login_required
def calendar():
    lawns = current_user.lawn_profiles.all()
    lawn_id = request.args.get('lawn_id', type=int)

    selected_lawn = None
    if lawn_id:
        selected_lawn = LawnProfile.query.filter_by(id=lawn_id, user_id=current_user.id).first()
    if not selected_lawn and lawns:
        selected_lawn = lawns[0]

    # Aktuális hónap
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # Összes esemény a hónapra
    events = []
    if selected_lawn:
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        start = date(year, month, 1)
        end = date(year, month, days_in_month)

        for log in selected_lawn.watering_logs.filter(
                WateringLog.date.between(start, end)).all():
            events.append({'date': log.date.isoformat(), 'type': 'watering',
                           'label': '💧 Öntözés', 'color': '#3b82f6'})
        for log in selected_lawn.mowing_logs.filter(
                MowingLog.date.between(start, end)).all():
            events.append({'date': log.date.isoformat(), 'type': 'mowing',
                           'label': '✂️ Nyírás', 'color': '#10b981'})
        for log in selected_lawn.fertilizing_logs.filter(
                FertilizingLog.date.between(start, end)).all():
            events.append({'date': log.date.isoformat(), 'type': 'fertilizing',
                           'label': '🌱 Trágyázás', 'color': '#f59e0b'})
        for log in selected_lawn.aeration_logs.filter(
                AerationLog.date.between(start, end)).all():
            events.append({'date': log.date.isoformat(), 'type': 'aeration',
                           'label': '🌬️ Szellőztetés', 'color': '#8b5cf6'})
        for log in selected_lawn.weed_logs.filter(
                WeedLog.date.between(start, end)).all():
            events.append({'date': log.date.isoformat(), 'type': 'weed',
                           'label': '🌿 Gyomirtás', 'color': '#ef4444'})

    return render_template('calendar.html',
                           lawns=lawns,
                           selected_lawn=selected_lawn,
                           events=events,
                           year=year,
                           month=month)


# =============================================================================
# API ENDPOINTOK (AJAX)
# =============================================================================

@app.route('/api/grass-product/<int:product_id>')
@login_required
def api_grass_product(product_id):
    """Visszaadja egy fűmag termék adatait JSON-ban (auto-kitöltéshez)."""
    product = GrassSeedProduct.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'brand': product.brand,
        'product_name': product.product_name,
        'grass_types': product.grass_types,
        'usage': product.usage,
        'description': product.description,
    })


@app.route('/api/fertilizer-product/new', methods=['POST'])
@login_required
def api_fertilizer_product_new():
    """Új műtrágya termék létrehozása AJAX-on keresztül (profil formból)."""
    data = request.get_json(silent=True) or {}
    brand = (data.get('brand') or '').strip()
    product_name = (data.get('product_name') or '').strip()
    npk = (data.get('npk') or '').strip()
    npk_n = data.get('npk_n') or 0.0
    npk_p = data.get('npk_p') or 0.0
    npk_k = data.get('npk_k') or 0.0
    fertilizer_type = (data.get('fertilizer_type') or '').strip()
    season = (data.get('season') or '').strip()

    if not brand or not product_name:
        return jsonify({'error': 'A márka és a terméknév kötelező.'}), 400

    # Duplikáció ellenőrzés
    existing = FertilizerProduct.query.filter_by(brand=brand, product_name=product_name).first()
    if existing:
        return jsonify({
            'id': existing.id,
            'brand': existing.brand,
            'product_name': existing.product_name,
            'npk': existing.npk,
            'npk_n': existing.npk_n,
            'npk_p': existing.npk_p,
            'npk_k': existing.npk_k,
            'fertilizer_type': existing.fertilizer_type,
            'already_exists': True,
        })

    product = FertilizerProduct(
        brand=brand,
        product_name=product_name,
        npk=npk or f"{int(npk_n)}-{int(npk_p)}-{int(npk_k)}",
        npk_n=float(npk_n),
        npk_p=float(npk_p),
        npk_k=float(npk_k),
        fertilizer_type=fertilizer_type or None,
        season=season or None,
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({
        'id': product.id,
        'brand': product.brand,
        'product_name': product.product_name,
        'npk': product.npk,
        'npk_n': product.npk_n,
        'npk_p': product.npk_p,
        'npk_k': product.npk_k,
        'fertilizer_type': product.fertilizer_type,
        'already_exists': False,
    }), 201


@app.route('/api/fertilizer-product/<int:product_id>')
@login_required
def api_fertilizer_product(product_id):
    """Visszaadja egy műtrágya termék adatait JSON-ban (auto-kitöltéshez)."""
    product = FertilizerProduct.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'brand': product.brand,
        'product_name': product.product_name,
        'npk': product.npk,
        'npk_n': product.npk_n,
        'npk_p': product.npk_p,
        'npk_k': product.npk_k,
        'fertilizer_type': product.fertilizer_type,
        'season': product.season,
        'description': product.description,
    })


# =============================================================================
# HIBAKEZELÉS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


# =============================================================================
# ALKALMAZÁS INDÍTÁS
# =============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products(app)
        # Uploads mappa létrehozása
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
