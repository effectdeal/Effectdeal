"""Operational status is derived from linked jobs; no guessing from an address."""
from datetime import date, datetime
from zoneinfo import ZoneInfo


def today():
    return datetime.now(ZoneInfo('Europe/Prague')).date().isoformat()


def valid_date(value):
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        raise ValueError('Vyplňte platné datum.')


def overlaps(vehicle, start, end=None):
    if vehicle.get('status') != 'unavailable':
        return False
    return vehicle.get('unavailableFrom', '') <= (end or start) and vehicle.get('unavailableTo', '') >= start


def vehicle_view(vehicle, transfers, rentals):
    result = dict(vehicle)
    result['baseStatus'] = vehicle.get('status', 'available')
    day = today()
    jobs = [t for t in transfers if t.get('vehicleId') == vehicle['id']]
    active = next((t for t in jobs if t.get('status') == 'progress'), None)
    scheduled = sorted((t for t in jobs if t.get('status') == 'assigned'), key=lambda t: (t.get('date',''),t.get('time','')))
    completed = sorted((t for t in jobs if t.get('status') == 'completed' and t.get('completedAt') and t.get('type')!='inspection'), key=lambda t:t['completedAt'], reverse=True)
    if completed and completed[0]['completedAt'] > vehicle.get('locationUpdatedAt', vehicle.get('createdAt','')):
        result['location'] = completed[0]['to']
        result['locationSource'] = 'transfer'
    if result['baseStatus'] == 'unavailable':
        result['status'] = 'unavailable' if overlaps(vehicle, day) else 'available'
    if result['status'] in ('unverified','service','unavailable'):
        return result
    if active:
        result.update(status='inspecting' if active.get('type')=='inspection' else 'delivering', activeTransferId=active['id'], destination=active.get('to',''))
    elif any(r.get('vehicleId')==vehicle['id'] and r.get('status')=='active' and r.get('start','')<=day<=r.get('end','') for r in rentals):
        result['status']='rented'
    elif scheduled:
        result.update(status='delivery_scheduled', activeTransferId=scheduled[0]['id'], destination=scheduled[0].get('to',''))
    return result
