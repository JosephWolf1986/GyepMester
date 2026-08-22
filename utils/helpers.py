"""utils/helpers.py – Képfeltöltés és egyéb segédfüggvények."""
import os
import uuid
from datetime import date
from PIL import Image


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_photo(file_obj, upload_folder, allowed_extensions, max_size=(1200, 1200)):
    """
    Képfájl mentése és átméretezése.
    Visszaadja a fájlnevet (nem a teljes útvonalat).
    """
    if not file_obj or not file_obj.filename:
        return None
    if not allowed_file(file_obj.filename, allowed_extensions):
        return None

    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, filename)

    os.makedirs(upload_folder, exist_ok=True)

    # Pillow átméretezés
    img = Image.open(file_obj)
    img.thumbnail(max_size, Image.LANCZOS)

    # EXIF orientáció javítás
    try:
        import piexif
        exif_data = img.info.get('exif', b'')
        if exif_data:
            exif_dict = piexif.load(exif_data)
            orientation = exif_dict.get('0th', {}).get(piexif.ImageIFD.Orientation, 1)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass

    # WebP formátumba konvertálás a kisebb méretért
    if ext in ('jpg', 'jpeg', 'png'):
        filename = filename.rsplit('.', 1)[0] + '.webp'
        filepath = os.path.join(upload_folder, filename)
        img.save(filepath, 'WEBP', quality=85)
    else:
        img.save(filepath)

    return filename


def delete_photo(filename, upload_folder):
    """Törli a képfájlt a szerveren."""
    if not filename:
        return
    filepath = os.path.join(upload_folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def days_since(log_date):
    """
    Visszaadja, hogy hány napja volt az esemény.
    log_date lehet datetime.date vagy None.
    """
    if log_date is None:
        return None
    if hasattr(log_date, 'date'):
        log_date = log_date.date()
    delta = date.today() - log_date
    return delta.days
