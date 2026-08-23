from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# =============================================================================
# BEÉPÍTETT TERMÉK KATALÓGUSOK
# =============================================================================

class GrassSeedProduct(db.Model):
    """Fűmag termékek katalógusa (beépített, csak olvasható)."""
    __tablename__ = 'grass_seed_product'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)           # Barenbrug, DLF Turfline, stb.
    product_name = db.Column(db.String(150), nullable=False)    # Water Saver, Sport, stb.
    grass_types = db.Column(db.String(300), nullable=False)     # Vesszővel elválasztott típusok
    usage = db.Column(db.String(150))                           # Szárazságtűrő, Sport, Díszgyep...
    description = db.Column(db.Text)

    # Kapcsolat a gyep profilokhoz
    lawn_profiles = db.relationship('LawnProfile', backref='seed_product', lazy='dynamic')

    def __repr__(self):
        return f'<GrassSeedProduct {self.brand} – {self.product_name}>'

    def grass_type_list(self):
        """Visszaadja a fűtípusokat listaként."""
        return [t.strip() for t in self.grass_types.split(',')]


class FertilizerProduct(db.Model):
    """Műtrágya termékek katalógusa (beépített, csak olvasható)."""
    __tablename__ = 'fertilizer_product'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)           # ICL, Compo, Genezis, stb.
    product_name = db.Column(db.String(150), nullable=False)    # All Round, Maintenance, stb.
    npk = db.Column(db.String(30), nullable=False)              # pl. "24-5-8"
    npk_n = db.Column(db.Float, nullable=False, default=0)      # Nitrogén %
    npk_p = db.Column(db.Float, nullable=False, default=0)      # Foszfor %
    npk_k = db.Column(db.Float, nullable=False, default=0)      # Kálium %
    fertilizer_type = db.Column(db.String(100))                 # Nitrogéndús, Káliumdús, Komplex...
    season = db.Column(db.String(100))                          # Tavasz, Ősz, Egész szezon...
    description = db.Column(db.Text)

    # Kapcsolat a naplóbejegyzésekkel
    fertilizing_logs = db.relationship('FertilizingLog', backref='fertilizer_product', lazy='dynamic')

    def __repr__(self):
        return f'<FertilizerProduct {self.brand} – {self.product_name} ({self.npk})>'


# =============================================================================
# FELHASZNÁLÓ
# =============================================================================

class User(UserMixin, db.Model):
    """Felhasználói fiók."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Kapcsolat a gyep profilokhoz
    lawn_profiles = db.relationship('LawnProfile', backref='owner', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# =============================================================================
# GYEP PROFIL
# =============================================================================

class LawnProfile(db.Model):
    """Egy gyep / kertterület profilja."""
    __tablename__ = 'lawn_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(150), nullable=False)            # pl. "Elülső kert"
    area_sqm = db.Column(db.Float, nullable=False)              # m²
    location_city = db.Column(db.String(100), nullable=False)   # Város

    # Fűtípus – termékből vagy kézzel
    grass_seed_product_id = db.Column(db.Integer, db.ForeignKey('grass_seed_product.id'), nullable=True)
    grass_type = db.Column(db.String(300))                      # Szabad szöveges fűtípus
    grass_type_source = db.Column(db.String(20), default='manual')  # 'manual' vagy 'product'

    # Egyéb jellemzők
    soil_type = db.Column(db.String(50))    # Homokos, Agyagos, Vályogos, Tőzeges
    sun_exposure = db.Column(db.String(50)) # Teljes nap, Félárnyas, Árnyékos
    cultivation_method = db.Column(db.String(50))  # Extenzív, Normál, Intenzív
    mowing_method = db.Column(db.String(50))       # Kézi, Gépi (fűnyíró)

    # Gyep állapota & vetés
    lawn_stage = db.Column(db.String(50), default='Meglévő, beállt gyep')  # 'Vetés előtt áll', 'Friss vetés / Felülvetés', 'Meglévő, beállt gyep'
    seeding_date = db.Column(db.Date)              # Vetés dátuma (ha friss vetés)

    # Fűnyírókés előzmény
    blade_sharpened_at = db.Column(db.Date)        # Utolsó élezés dátuma

    # Fotó
    photo = db.Column(db.String(255))       # Fájlnév a static/uploads/ mappában

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Kapcsolatok (naplók)
    watering_logs = db.relationship('WateringLog', backref='lawn', lazy='dynamic',
                                     cascade='all, delete-orphan')
    mowing_logs = db.relationship('MowingLog', backref='lawn', lazy='dynamic',
                                   cascade='all, delete-orphan')
    fertilizing_logs = db.relationship('FertilizingLog', backref='lawn', lazy='dynamic',
                                        cascade='all, delete-orphan')
    aeration_logs = db.relationship('AerationLog', backref='lawn', lazy='dynamic',
                                     cascade='all, delete-orphan')
    weed_logs = db.relationship('WeedLog', backref='lawn', lazy='dynamic',
                                 cascade='all, delete-orphan')
    pest_logs = db.relationship('PestLog', backref='lawn', lazy='dynamic',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LawnProfile {self.name} ({self.area_sqm} m²)>'

    def last_watering(self):
        return self.watering_logs.order_by(WateringLog.date.desc()).first()

    def last_mowing(self):
        return self.mowing_logs.order_by(MowingLog.date.desc()).first()

    def last_fertilizing(self):
        return self.fertilizing_logs.order_by(FertilizingLog.date.desc()).first()

    def last_aeration(self):
        return self.aeration_logs.order_by(AerationLog.date.desc()).first()


# =============================================================================
# NAPLÓK
# =============================================================================

class WateringLog(db.Model):
    """Öntözési napló."""
    __tablename__ = 'watering_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    duration_min = db.Column(db.Integer)                # Időtartam (perc)
    amount_liters = db.Column(db.Float)                 # l/m²
    method = db.Column(db.String(50))                   # Kézi, Öntözőrendszer, Szórófej
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WateringLog {self.date}>'


class MowingLog(db.Model):
    """Fűnyírási napló."""
    __tablename__ = 'mowing_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    height_cm = db.Column(db.Float)                     # Vágási magasság (cm)
    condition_before = db.Column(db.String(50))         # Jó, Hosszú, Száraz, Nedves
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MowingLog {self.date} – {self.height_cm} cm>'


class FertilizingLog(db.Model):
    """Trágyázási napló."""
    __tablename__ = 'fertilizing_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

    # Termékből vagy kézzel
    fertilizer_product_id = db.Column(db.Integer, db.ForeignKey('fertilizer_product.id'), nullable=True)
    fertilizer_type = db.Column(db.String(100))         # Nitrogéndús, Káliumdús, Komplex, Szerves
    fertilizer_type_source = db.Column(db.String(20), default='manual')  # 'manual' vagy 'product'

    # NPK értékek (kézzel vagy termékből)
    npk_n = db.Column(db.Float)
    npk_p = db.Column(db.Float)
    npk_k = db.Column(db.Float)

    amount_per_sqm = db.Column(db.Float)                # g/m²
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FertilizingLog {self.date} – {self.fertilizer_type}>'

    def npk_string(self):
        if self.npk_n is not None:
            return f"{int(self.npk_n or 0)}-{int(self.npk_p or 0)}-{int(self.npk_k or 0)}"
        return "–"


class AerationLog(db.Model):
    """Szellőztetési napló."""
    __tablename__ = 'aeration_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    method = db.Column(db.String(100))                  # Tüskés villa, Szellőztető gép, Lyukasztó
    overseeded = db.Column(db.Boolean, default=False)   # Volt-e felülvetés?
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AerationLog {self.date}>'


class WeedLog(db.Model):
    """Gyomirtási napló."""
    __tablename__ = 'weed_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    method = db.Column(db.String(50))                   # Kézi, Vegyszeres, Mechanikus
    product_name = db.Column(db.String(150))
    severity = db.Column(db.String(30))                 # Enyhe, Közepes, Súlyos
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WeedLog {self.date} – {self.severity}>'


class PestLog(db.Model):
    """Kártevő / betegség megfigyelési napló."""
    __tablename__ = 'pest_log'

    id = db.Column(db.Integer, primary_key=True)
    lawn_id = db.Column(db.Integer, db.ForeignKey('lawn_profile.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    pest_type = db.Column(db.String(100))               # Gombás betegség, Rovarkár, Vakond, Egyéb
    severity = db.Column(db.String(30))                 # Enyhe, Közepes, Súlyos
    treatment = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PestLog {self.date} – {self.pest_type}>'
