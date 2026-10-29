"""Import the reviewed public snapshot, without overwriting local fleet records."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from ..storage import Conflict


def read_catalog(directory):
    return json.loads((Path(directory)/'effectdeal-catalog.json').read_text(encoding='utf-8'))


def import_vehicle(store, tenant, source, directory):
    source_id=source['id']
    existing=store.get(tenant,'vehicles',source_id)
    if existing and existing.get('sourceSystem')!='effectdeal.com':
        raise Conflict('ID nabídky je obsazené jiným vozidlem.')
    directory=Path(directory).resolve()
    # Validate every local image before the first write. No remote URL is fetched by the API.
    images=[]
    for photo in source['photos']:
        path=(directory/photo['file']).resolve()
        if not path.is_relative_to(directory):raise ValueError('Neplatná cesta fotografie.')
        blob=path.read_bytes()
        if hashlib.sha256(blob).hexdigest()!=photo['sha256']:raise ValueError('Fotografie v balíčku je poškozená.')
        images.append((photo,blob))
    timestamp=datetime.now(timezone.utc).isoformat()
    vehicle={k:v for k,v in source.items() if k!='photos'}
    vehicle.update(createdAt=timestamp,updatedAt=timestamp)
    created=False
    if not existing:
        try:store.create(tenant,'vehicles',vehicle);created=True
        except Conflict:pass  # Concurrent/repeated imports use the same deterministic ID.
    docs=[d for d in store.list(tenant,'documents') if d.get('parentKind')=='vehicles' and d.get('parentId')==source_id]
    count=len(docs);added=0;skipped=0;cover=None
    for photo,blob in images:
        document_id='web-photo-'+hashlib.sha256((source_id+'/'+photo['file']).encode()).hexdigest()
        found=store.get(tenant,'documents',document_id)
        if not found:
            if count>=10:skipped+=1;continue
            record={'id':document_id,'parentKind':'vehicles','parentId':source_id,
                    'name':photo['name'],'mime':photo['mime'],'size':len(blob),'createdAt':timestamp,
                    'content':base64.b64encode(blob).decode(),'sourceUrl':photo['sourceUrl']}
            try:store.create(tenant,'documents',record);added+=1;count+=1
            except Conflict:pass
        if cover is None:cover=document_id
    current=store.get(tenant,'vehicles',source_id)
    if cover and not current.get('profileDocumentId'):
        current['profileDocumentId']=cover;current['updatedAt']=timestamp
        try:store.update(tenant,'vehicles',current,current['version'])
        except Conflict:pass
    return {'vehicleId':source_id,'created':created,'addedPhotos':added,'skippedPhotos':skipped}
