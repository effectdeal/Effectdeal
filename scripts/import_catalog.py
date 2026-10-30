"""One-time, resumable production import: python -m scripts.import_catalog."""
import hashlib
import os
from pathlib import Path

from app.domain.catalog import import_vehicle, read_catalog
from app.storage import Conflict, MongoStore


def run_import(store, directory):
    directory = Path(directory)
    marker_id = 'effectdeal-catalog-' + hashlib.sha256(
        (directory / 'effectdeal-catalog.json').read_bytes()).hexdigest()
    if store.get('company', 'imports', marker_id):
        print('Katalog již byl importován. Data zůstávají beze změny.', flush=True)
        return False
    catalog = read_catalog(directory)
    # Check the entire bundle before writing any vehicle.
    for vehicle in catalog['items']:
        for photo in vehicle['photos']:
            path = (directory / photo['file']).resolve()
            if not path.is_relative_to(directory.resolve()):
                raise ValueError('Neplatná cesta fotografie.')
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != photo['sha256']:
                raise ValueError('Chybí nebo je poškozená fotografie: ' + photo['file'])
    for index, vehicle in enumerate(catalog['items'], 1):
        result = import_vehicle(store, 'company', vehicle, directory)
        if result['skippedPhotos']:
            raise ValueError('Vozidlo má již limit 10 fotografií. Dokončete import v administraci.')
        print(f"Import {index}/{len(catalog['items'])}: {vehicle['brand']} {vehicle['model']}", flush=True)
    try:
        store.create('company', 'imports', {'id': marker_id, 'vehicles': len(catalog['items'])})
    except Conflict:
        pass
    print('Import do společné databáze dokončen.', flush=True)
    return True


def main():
    if os.getenv('APP_MODE') != 'production' or not os.getenv('MONGODB_URI'):
        raise SystemExit('Import vyžaduje APP_MODE=production a MONGODB_URI.')
    store = MongoStore(os.environ['MONGODB_URI'], os.getenv('MONGODB_DATABASE', 'effectdeal'))
    try:
        run_import(store, Path(__file__).resolve().parents[1] / 'app' / 'data')
    finally:
        store.client.close()


if __name__ == '__main__':
    main()
