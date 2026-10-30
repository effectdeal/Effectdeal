import base64
import functools
import secrets
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from flask import Blueprint, current_app, g, jsonify, request, session, abort, Response, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from ..domain.calculations import number, report_totals
from ..domain.seeds import seed
from ..domain.employees import profile, username
from ..storage import Conflict
from ..request_store import RequestStore
from ..domain.fleet import vehicle_view, overlaps, valid_date, today

api=Blueprint('api',__name__)
KINDS={'employees','vehicles','customers','rentals','transfers','reports','notifications','handover','documents','service','invoices','payments'}
ROLES={'owner','manager','dispatcher','employee'}
STAFF={'owner','manager','dispatcher'}
def store():
    if not hasattr(g,'request_store'):g.request_store=RequestStore(current_app.extensions['store'])
    return g.request_store
def now(): return datetime.now(timezone.utc).isoformat()
def public(record,kind=None):
    if kind=='employees' or ('role' in record and 'email' in record):record=profile(record)
    if kind=='vehicles':record=vehicle_view(record,store().list(g.tenant,'transfers'),store().list(g.tenant,'rentals'))
    r={k:v for k,v in record.items() if k not in ('passwordHash','password','content')}
    # Personal roles do not receive company prices, even in API responses.
    if getattr(g,'user',None) and g.user.get('role') not in STAFF and kind=='vehicles':
        for key in ('monthlyPrice','priceOriginal','promoLabel'):r.pop(key,None)
        if r.get('activeTransferId') and not any(t['id']==r['activeTransferId'] and t.get('employeeId')==g.user['id'] for t in store().list(g.tenant,'transfers')):
            r.pop('activeTransferId',None);r.pop('destination',None)
    return r
def csrf():
    if request.method not in ('GET','HEAD','OPTIONS') and (not session.get('csrf') or request.headers.get('X-CSRF-Token')!=session.get('csrf')):
        abort(403,description='Obnovte stránku a zkuste to znovu.')
def login_required(fn):
    @functools.wraps(fn)
    def wrapped(*args,**kwargs):
        if not session.get('user'): abort(401,description='Přihlaste se prosím.')
        g.tenant=session['tenant'];g.user=store().get(g.tenant,'employees',session['user'])
        if not g.user or g.user.get('disabled') or g.user.get('role') not in ROLES: abort(401)
        csrf();return fn(*args,**kwargs)
    return wrapped

def scoped(kind,r):
    role=g.user['role'];uid=g.user['id']
    if kind=='notifications': return r.get('recipient')==uid or (role in STAFF and r.get('recipient')==role)
    if kind=='documents':
        parent_kind=r.get('parentKind')
        if parent_kind not in ('employees','reports','vehicles','handover','rentals'):return False
        parent=store().get(g.tenant,parent_kind,r.get('parentId',''))
        if not parent:return False
        if parent_kind=='employees':return private_profile(parent)
        return scoped(parent_kind,parent)
    if kind in ('invoices','payments') and role not in ('owner','manager'):return False
    if role in STAFF: return True
    if kind=='employees': return r['id']==uid
    if kind in ('reports','transfers','handover'): return r.get('employeeId')==uid
    if kind=='vehicles': return any(t.get('employeeId')==uid and t.get('vehicleId')==r['id'] for t in store().list(g.tenant,'transfers'))
    return False

def private_profile(employee):
    return (employee['id']==g.user['id'] or g.user['role']=='owner'
            or (g.user['role']=='manager' and employee.get('role')!='owner'))

def get_record(kind,id):
    if kind not in KINDS: abort(404)
    r=store().get(g.tenant,kind,id)
    if not r or not scoped(kind,r): abort(404)
    return r

def writable(kind,r=None):
    role=g.user['role']
    if r and not scoped(kind,r): abort(404)
    if kind in ('notifications','documents'): abort(403)
    if kind=='vehicles' and r is None and role not in ('owner','manager'):abort(403)
    if kind=='employees':
        if role not in ('owner','manager'): abort(403)
        if r and r.get('role')=='owner' and role!='owner': abort(403)
    elif kind in ('invoices','payments'):
        if role not in ('owner','manager'): abort(403)
    elif kind in ('reports','handover'):
        if r and kind=='reports' and r['status'] not in ('draft','returned'): abort(409,description='Odeslaný výkaz lze pouze schválit, zamítnout nebo vrátit.')
    elif role not in STAFF: abort(403)

FIELDS={
 'employees':{'name','firstName','lastName','phone','username','position','email','role','hourlyRate','available','latitude','longitude','locationConfirmedAt','disabled','password'},
 'vehicles':{'brand','model','plate','vin','year','color','drive','fuel','transmission','power','equipment','description','status','monthlyPrice','location','latitude','longitude','odometer','defects','lastRentalEnd','profileDocumentId','unavailableFrom','unavailableTo'},
 'customers':{'name','type','email','phone','address','companyId','note'},
 'rentals':{'customerId','vehicleId','start','end','monthlyPrice','deposit','status','note'},
 'transfers':{'rentalId','customerId','vehicleId','employeeId','from','to','date','time','status','type','note'},
 'reports':{'employeeId','transferId','vehicleId','title','legs','weekendBonus','holidayBonus','reward','overtimeMinutes','completedTasks','note'},
 'handover':{'transferId','vehicleId','employeeId','pickup','delivery','odometerStart','odometerEnd','fuelStart','fuelEnd','damages','customerName','signature','note'},
 'service':{'vehicleId','date','description','cost','nextDate'},
 'invoices':{'customerId','rentalId','number','amount','dueDate','status','note'},
 'payments':{'rentalId','invoiceId','amount','date','type','note'},
}
NUMERIC={'hourlyRate','monthlyPrice','deposit','power','year','odometer','odometerStart','odometerEnd','amount','cost','completedTasks','weekendBonus','holidayBonus','reward','overtimeMinutes'}
def validate(kind,payload,old=None):
    r={**(old or {}),**{k:v for k,v in payload.items() if k in FIELDS[kind]}}
    for k in NUMERIC & r.keys():
        r[k]=None if kind=='vehicles' and r[k] in (None,'') else float(number(r[k]))
    for k,v in r.items():
        if isinstance(v,str) and len(v)>10000 and k!='signature':raise ValueError('Text je příliš dlouhý.')
    role=g.user['role']
    if kind=='employees':
        r=profile(r)
        for key in ('firstName','lastName','email','phone','position'):
            if not isinstance(r.get(key),str):raise ValueError('Neplatná hodnota profilu: '+key)
            r[key]=r[key].strip()
        if not r['firstName'] or (not old and not r['lastName']):raise ValueError('Vyplňte jméno a příjmení.')
        if not old and not r['phone']:raise ValueError('Vyplňte kontakt (telefon).')
        if not old and not payload.get('username'):raise ValueError('Vyplňte uživatelské jméno.')
        r['name']=' '.join(filter(None,[r['firstName'],r['lastName']]))
        r['username']=username(r['username'])
        if r.get('role','employee') not in ROLES:raise ValueError('Neplatná role.')
        if role!='owner' and r.get('role')=='owner':abort(403)
        if old and old.get('role')=='owner':r['role']='owner';r['disabled']=False
        r.setdefault('hourlyRate',0);r.setdefault('role','employee');r['available']=r.get('available',True) in (True,'true','True')
        if not r.get('name') or '@' not in r.get('email',''):raise ValueError('Vyplňte jméno a e-mail.')
        r['email']=r['email'].strip().lower()
        if any(e['email']==r['email'] and e['id']!=r.get('id') for e in store().list(g.tenant,'employees')):raise ValueError('E-mail již existuje.')
        if any(profile(e)['username'].lower()==r['username'] and e['id']!=r.get('id') for e in store().list(g.tenant,'employees')):raise ValueError('Uživatelské jméno již existuje.')
        password=r.pop('password',None)
        if password:
            if not isinstance(password,str) or not 12<=len(password)<=200:raise ValueError('Heslo musí mít 12–200 znaků.')
            r['passwordHash']=generate_password_hash(password)
        if not old and not password:raise ValueError('Nový účet vyžaduje heslo.')
    if kind in ('vehicles','rentals') and role=='dispatcher':
        r['monthlyPrice']=(old or {}).get('monthlyPrice',0)
    if kind=='vehicles':
        if 'location' in payload and payload['location']!=(old or {}).get('location'):r['locationUpdatedAt']=now()
        for key in ('brand','model') if r.get('status')=='unverified' or r.get('sourceSystem')=='effectdeal.com' else ('brand','model','plate'):
            if not str(r.get(key,'')).strip():raise ValueError('Vyplňte značku, model a SPZ.')
        r.setdefault('status','available');r.setdefault('monthlyPrice',0)
        if old and r['status'] in ('delivering','delivery_scheduled','inspecting') and r['status']==vehicle_view(old,store().list(g.tenant,'transfers'),store().list(g.tenant,'rentals'))['status']:r['status']=old['status']
        if r['status'] not in ('unverified','available','rented','service','unavailable'):raise ValueError('Neplatný stav vozidla.')
        if r['status']=='unavailable':
            r['unavailableFrom']=valid_date(r.get('unavailableFrom'))
            r['unavailableTo']=valid_date(r.get('unavailableTo'))
            if r['unavailableTo']<r['unavailableFrom']:raise ValueError('Konec nedostupnosti nesmí být před začátkem.')
            for task in store().list(g.tenant,'transfers'):
                if task.get('vehicleId')==r.get('id') and task.get('status') in ('assigned','progress') and (task.get('status')=='progress' or overlaps(r,task.get('date') or today())):
                    raise ValueError('V tomto období má vozidlo přidělený převoz. Nejdříve převoz přesuňte nebo zrušte.')
            for rental in store().list(g.tenant,'rentals'):
                if rental.get('vehicleId')==r.get('id') and rental.get('status') in ('reserved','active') and overlaps(r,rental.get('start',''),rental.get('end','')):
                    raise ValueError('Nedostupnost se překrývá s pronájmem.')
        else:
            r.pop('unavailableFrom',None);r.pop('unavailableTo',None)
        if r['status']!='unverified' and not str(r.get('plate','')).strip():raise ValueError('Nejdříve doplňte skutečnou SPZ vozidla.')
        profile_id=r.get('profileDocumentId')
        if profile_id:
            photo=store().get(g.tenant,'documents',profile_id)
            if (not photo or photo.get('parentKind')!='vehicles'
                    or photo.get('parentId')!=r.get('id')
                    or photo.get('mime') not in ('image/jpeg','image/png','image/webp')):
                raise ValueError('Profilová fotografie musí patřit tomuto vozidlu.')
    for key,target in [('employeeId','employees'),('vehicleId','vehicles'),('customerId','customers'),('rentalId','rentals'),('transferId','transfers')]:
        if r.get(key) and not store().get(g.tenant,target,r[key]):raise ValueError('Navázaný záznam neexistuje: '+key)
    if kind=='rentals':
        if not r.get('customerId') or not r.get('vehicleId'):raise ValueError('Vyberte zákazníka a vozidlo.')
        vehicle=store().get(g.tenant,'vehicles',r['vehicleId'])
        if vehicle.get('status')=='unverified':raise ValueError('Nejdříve doplňte a ověřte vozidlo z nabídky.')
        if not r.get('start') or not r.get('end') or r['end']<=r['start']:raise ValueError('Konec pronájmu musí být po začátku.')
        r.setdefault('status','reserved')
        if r['status'] in ('reserved','active') and overlaps(vehicle,r['start'],r['end']):raise ValueError('Vozidlo je v tomto období nedostupné.')
    if kind=='transfers':
        rental=store().get(g.tenant,'rentals',r.get('rentalId',''))
        if rental:r['customerId']=rental['customerId'];r['vehicleId']=rental['vehicleId']
        if not r.get('vehicleId') or not r.get('employeeId') or not r.get('from') or not r.get('to'):raise ValueError('Vyplňte vozidlo, zaměstnance a trasu.')
        vehicle=store().get(g.tenant,'vehicles',r['vehicleId'])
        if vehicle.get('status')=='unverified':raise ValueError('Nejdříve doplňte a ověřte vozidlo z nabídky.')
        r.setdefault('status','assigned')
        if r['status'] not in ('assigned','progress','completed','cancelled'):raise ValueError('Neplatný stav převozu.')
        if r['status'] in ('assigned','progress'):
            if overlaps(vehicle,valid_date(r.get('date') or today())) or (r['status']=='progress' and overlaps(vehicle,today())):raise ValueError('Vozidlo je v tomto období nedostupné.')
            if vehicle.get('status')=='service':raise ValueError('Vozidlo je v servisu.')
            if r['status']=='progress' and any(t.get('vehicleId')==r['vehicleId'] and t['id']!=r.get('id') and t.get('status')=='progress' for t in store().list(g.tenant,'transfers')):raise ValueError('U vozidla již probíhá jiný převoz.')
        if old and old.get('status')=='completed' and r['status']!='completed':raise ValueError('Dokončený převoz nelze znovu otevřít.')
        if r['status']=='completed' and (not old or old.get('status')!='completed'):r['completedAt']=now()
        if old and old.get('reportId') and any(r.get(k)!=old.get(k) for k in ('employeeId','vehicleId','rentalId')):raise ValueError('Převoz již má výkaz. Přiřazení již nelze měnit.')
    if kind=='reports':
        if r.get('transferId'):
            transfer=store().get(g.tenant,'transfers',r['transferId'])
            if not scoped('transfers',transfer):abort(404)
            r['employeeId']=transfer['employeeId'];r['vehicleId']=transfer['vehicleId']
        if role not in STAFF:r['employeeId']=g.user['id']
        if role not in STAFF and r.get('vehicleId'):
            vehicle=store().get(g.tenant,'vehicles',r['vehicleId'])
            if not scoped('vehicles',vehicle):abort(404)
        r.setdefault('employeeId',g.user['id']);r.setdefault('status','draft')
        if not r.get('title') or not isinstance(r.get('legs'),list) or not 1<=len(r['legs'])<=30:raise ValueError('Výkaz potřebuje název a 1–30 úseků.')
        for leg in r['legs']:
            if not isinstance(leg,dict) or not all(leg.get(k) for k in ('date','from','to','method','purpose')):raise ValueError('Vyplňte datum, trasu, dopravu a účel všech cest.')
            number(leg.get('km'))
        e=store().get(g.tenant,'employees',r['employeeId'])
        if not e:raise ValueError('Zaměstnanec neexistuje.')
        r['hourlyRate']=e.get('hourlyRate',0);r['totals']=report_totals(r,r['hourlyRate'])
    if kind=='handover':
        t=store().get(g.tenant,'transfers',r.get('transferId',''))
        if not t or not scoped('transfers',t):abort(404)
        r['vehicleId']=t['vehicleId'];r['employeeId']=t['employeeId']
        if r.get('odometerEnd',0)<r.get('odometerStart',0):raise ValueError('Konečný tachometr nemůže být nižší.')
        if r.get('signature') and (not r['signature'].startswith('data:image/png;base64,') or len(r['signature'])>300000):raise ValueError('Neplatný podpis.')
    return r

@api.get('/health')
def health():return jsonify(status='ok',app='EFFECT DEAL',version='0.3.1')
@api.get('/session')
def session_info():
    session.setdefault('csrf',secrets.token_hex(24))
    user=store().get(session.get('tenant',''), 'employees',session['user']) if session.get('user') else None
    return jsonify(user=public(user) if user and not user.get('disabled') and user.get('role') in ROLES else None,csrf=session['csrf'],mode=current_app.config['APP_MODE'])
@api.post('/login')
def login():
    csrf();p=request.get_json() or {}
    if current_app.config['APP_MODE']=='demo':
        role=p.get('role','owner');ids={'owner':'owner','dispatcher':'dispatcher','employee':'driver'}
        if role not in ids:abort(400)
        tenant=session.get('tenant') or 'demo-'+uuid4().hex
        seed(store(),tenant);session['tenant']=tenant;session['user']=ids[role]
    else:
        tenant='company';users=store().list(tenant,'employees')
        login_name=str(p.get('username',p.get('email',''))).strip().lower()
        u=next((u for u in users if profile(u)['username'].lower()==login_name),None)
        if not u or u.get('disabled') or u.get('role') not in ROLES or not check_password_hash(u.get('passwordHash',''),str(p.get('password',''))):abort(401,description='Neplatné přihlašovací údaje.')
        session.clear();session['tenant']=tenant;session['user']=u['id']
    session['csrf']=secrets.token_hex(24)
    return jsonify(user=public(store().get(tenant,'employees',session['user'])),csrf=session['csrf'])
@api.post('/logout')
@login_required
def logout():
    tenant=session.get('tenant');session.clear()
    if current_app.config['APP_MODE']=='demo':session['tenant']=tenant
    return jsonify(ok=True)
@api.get('/<kind>')
@login_required
def listing(kind):
    if kind not in KINDS:abort(404)
    filters={}
    if kind=='documents':
        filters={k:request.args[k] for k in ('parentKind','parentId') if request.args.get(k)}
    if kind=='service' and request.args.get('vehicleId'):filters['vehicleId']=request.args['vehicleId']
    if kind=='handover' and request.args.get('transferId'):filters['transferId']=request.args['transferId']
    if g.user['role']=='employee' and kind in ('reports','transfers','handover'):filters['employeeId']=g.user['id']
    raw=store().list(g.tenant,kind,filters)
    if kind=='documents' and not filters.get('parentId'):
        for parent_kind in {r.get('parentKind') for r in raw} & {'vehicles','reports','employees','rentals','handover'}:
            store().list(g.tenant,parent_kind)
    rows=[public(r,kind) for r in raw if scoped(kind,r)]
    search=request.args.get('q','').lower();status=request.args.get('status');employee=request.args.get('employeeId')
    rows=[r for r in rows if (not search or search in str(r).lower()) and (not status or r.get('status')==status) and (not employee or r.get('employeeId')==employee)]
    if kind=='documents':
        for key in ('parentKind','parentId'):
            if request.args.get(key):rows=[r for r in rows if r.get(key)==request.args[key]]
    rows.sort(key=lambda r:r.get('updatedAt',r.get('createdAt','')),reverse=True)
    limit=min(max(int(request.args.get('limit',50)),1),100);offset=max(int(request.args.get('offset',0)),0)
    return jsonify(items=rows[offset:offset+limit],total=len(rows))
@api.get('/<kind>/<id>')
@login_required
def detail(kind,id):return jsonify(public(get_record(kind,id),kind))
@api.post('/<kind>')
@login_required
def create(kind):
    if kind not in FIELDS:abort(404)
    writable(kind);p=request.get_json() or {};r=validate(kind,p);r.update(id=uuid4().hex,createdAt=now(),updatedAt=now())
    r=store().create(g.tenant,kind,r)
    return jsonify(public(r,kind)),201
@api.put('/<kind>/<id>')
@login_required
def update(kind,id):
    if kind not in FIELDS:abort(404)
    old=get_record(kind,id);writable(kind,old);p=request.get_json() or {}
    if p.get('version')!=old['version']:raise Conflict('Záznam je zastaralý. Obnovte ho.')
    r=validate(kind,p,old);r['updatedAt']=now();r=store().update(g.tenant,kind,r,old['version'])
    return jsonify(public(r,kind))
@api.post('/transfers/<id>/status')
@login_required
def transfer_status(id):
    old=get_record('transfers',id);p=request.get_json() or {}
    if p.get('version')!=old['version']:raise Conflict('Záznam je zastaralý. Obnovte ho.')
    target=p.get('status')
    allowed={'assigned':{'progress','cancelled'},'progress':{'completed','cancelled'}}
    if target not in allowed.get(old.get('status'),set()):abort(409,description='Neplatný přechod stavu převozu.')
    if g.user['role']=='employee' and target=='cancelled':abort(403)
    record=validate('transfers',{'status':target},old);record['updatedAt']=now()
    record=store().update(g.tenant,'transfers',record,old['version'])
    return jsonify(public(record,'transfers'))

@api.post('/transfers/<id>/report')
@login_required
def transfer_report(id):
    t=get_record('transfers',id);rid='report-'+id
    existing=store().get(g.tenant,'reports',rid)
    if existing:return jsonify(public(existing))
    v=store().get(g.tenant,'vehicles',t['vehicleId'])
    r=validate('reports',{'employeeId':t['employeeId'],'vehicleId':t['vehicleId'],'transferId':id,'title':'Převoz '+v['plate']+' · '+t['from']+' → '+t['to'],'legs':[{'date':t.get('date') or now()[:10],'from':t['from'],'to':t['to'],'method':'Služební vozidlo','purpose':t.get('note') or 'Převoz vozidla','minutes':0,'breakMinutes':0,'km':0}]})
    r.update(id=rid,createdAt=now(),updatedAt=now())
    try:r=store().create(g.tenant,'reports',r)
    except Conflict:r=store().get(g.tenant,'reports',rid)
    t['reportId']=rid
    try:store().update(g.tenant,'transfers',t,t['version'])
    except Conflict:pass
    return jsonify(public(r)),201
@api.post('/reports/<id>/action')
@login_required
def report_action(id):
    r=get_record('reports',id);p=request.get_json() or {};action=p.get('action');role=g.user['role']
    if p.get('version')!=r['version']:raise Conflict('Obnovte výkaz před změnou stavu.')
    if action=='submit':
        if r['status'] not in ('draft','returned'):abort(409)
        if role not in STAFF and r['employeeId']!=g.user['id']:abort(403)
        r=validate('reports',r,r);r['status']='submitted';r['submittedAt']=now()
    elif action in ('approve','reject','return'):
        if role not in STAFF:abort(403)
        if role=='dispatcher' and (not r.get('transferId') or r['employeeId']==g.user['id']):abort(403)
        if r['status']!='submitted':abort(409)
        if action!='approve' and not str(p.get('reason','')).strip():raise ValueError('Vyplňte důvod zamítnutí nebo vrácení.')
        r['status']={'approve':'approved','reject':'rejected','return':'returned'}[action];r['reviewNote']=p.get('reason','');r['reviewedBy']=g.user['id'];r['reviewedAt']=now()
    else:abort(400)
    r['updatedAt']=now();r=store().update(g.tenant,'reports',r,r['version'])
    recipient='owner' if action=='submit' else r['employeeId']
    nid=id+'-'+str(r['version'])
    store().create(g.tenant,'notifications',{'id':nid,'recipient':recipient,'reportId':id,'title':'Nevyřízený výkaz' if action=='submit' else 'Výkaz: '+r['status'],'read':False,'createdAt':now()})
    return jsonify(public(r))
@api.post('/notifications/<id>/read')
@login_required
def read_notification(id):
    r=get_record('notifications',id)
    if not r.get('read'):r['read']=True;store().update(g.tenant,'notifications',r,r['version'])
    return jsonify(ok=True)
@api.post('/documents/upload')
@login_required
def upload():
    kind=request.form.get('parentKind');id=request.form.get('parentId')
    if kind not in ('employees','reports','vehicles','handover','rentals'):abort(400)
    parent=get_record(kind,id)
    if kind=='employees' and not private_profile(parent):abort(403)
    if kind=='reports' and parent['status'] not in ('draft','returned'):abort(409)
    if kind in ('vehicles','rentals') and g.user['role'] not in STAFF:abort(403)
    f=request.files.get('file')
    if not f:raise ValueError('Vyberte soubor.')
    content=f.read(10*1024*1024+1)
    if len(content)>10*1024*1024:abort(413)
    mime=f.mimetype
    signatures={'image/jpeg':content[:3]==b'\xff\xd8\xff','image/png':content[:8]==b'\x89PNG\r\n\x1a\n','application/pdf':content[:5]==b'%PDF-','image/webp':content[:4]==b'RIFF' and content[8:12]==b'WEBP'}
    if not signatures.get(mime):raise ValueError('Povolené soubory: JPG, PNG, WebP a PDF.')
    if kind=='vehicles' and mime=='application/pdf':raise ValueError('Fotografie vozidla musí být obrázek.')
    count=len(store().list(g.tenant,'documents',{'parentKind':kind,'parentId':id}))
    if count>=10:raise ValueError('Nejvýše 10 příloh na záznam.')
    # Files stay behind authenticated API; Mongo document is capped below 16 MB.
    r=store().create(g.tenant,'documents',{'id':uuid4().hex,'parentKind':kind,'parentId':id,'name':f.filename[:150],'mime':mime,'size':len(content),'createdAt':now(),'content':base64.b64encode(content).decode()})
    if kind=='vehicles':
        # First uploaded image becomes the cover; later uploads preserve the choice.
        vehicle=store().get(g.tenant,'vehicles',id)
        if not vehicle.get('profileDocumentId'):
            vehicle['profileDocumentId']=r['id'];vehicle['updatedAt']=now()
            try:store().update(g.tenant,'vehicles',vehicle,vehicle['version'])
            except Conflict:pass  # A concurrent edit wins; the uploaded image remains selectable.
    return jsonify(public(r)),201
@api.get('/documents/<id>/file')
@login_required
def document_file(id):
    metadata=store().list(g.tenant,'documents',{'id':id})
    if not metadata or not scoped('documents',metadata[0]):abort(404)
    r=metadata[0]
    image=r['mime'] in ('image/jpeg','image/png','image/webp')
    if image and request.args.get('size')=='thumb':
        from ..image_cache import thumbnail_path
        path=thumbnail_path(g.tenant,r,lambda:base64.b64decode(store().get(g.tenant,'documents',id)['content']))
        if path:
            response=send_file(path,mimetype='image/webp',conditional=True,max_age=0)
            response.headers['Cache-Control']='private, no-cache'
            return response
    r=store().get(g.tenant,'documents',id)
    disposition='inline' if image and request.args.get('download')!='1' else 'attachment'
    response=Response(base64.b64decode(r['content']),mimetype=r['mime'],headers={'Content-Disposition':disposition+'; filename=document'})
    response.set_etag(r['id']+'-'+str(r['version']))
    response.make_conditional(request)
    response.headers['Cache-Control']='no-store'
    return response

def catalog_directory():
    return Path(current_app.config.get('CATALOG_DIRECTORY',Path(current_app.root_path)/'data'))

@api.get('/catalog/effectdeal')
@login_required
def catalog_preview():
    if g.user['role'] not in ('owner','manager'):abort(403)
    from ..domain.catalog import read_catalog
    catalog=read_catalog(catalog_directory())
    items=[]
    existing={v['id'] for v in store().list(g.tenant,'vehicles')}
    for item in catalog['items']:
        items.append({k:item.get(k) for k in ('id','sourceSlug','brand','model','year','monthlyPrice','sourceUrl')})
        items[-1].update(photoCount=len(item['photos']),imported=item['id'] in existing)
    return jsonify(items=items,fetchedAt=catalog['fetchedAt'],source=catalog['source'])

@api.post('/catalog/effectdeal/<slug>/import')
@login_required
def catalog_import(slug):
    if g.user['role'] not in ('owner','manager'):abort(403)
    from ..domain.catalog import read_catalog,import_vehicle
    catalog=read_catalog(catalog_directory())
    source=next((r for r in catalog['items'] if r['sourceSlug']==slug),None)
    if source is None:abort(404)
    return jsonify(import_vehicle(store(),g.tenant,source,catalog_directory()))

@api.get('/dashboard')
@login_required
def dashboard():
    if g.user['role'] not in STAFF:abort(403)
    vehicles=store().list(g.tenant,'vehicles')
    transfers=store().list(g.tenant,'transfers')
    reports=store().list(g.tenant,'reports')
    mail=[r for r in store().list(g.tenant,'notifications') if scoped('notifications',r)]
    recent=sorted(transfers,key=lambda r:r.get('updatedAt',r.get('createdAt','')),reverse=True)[:6]
    return jsonify(vehicleCount=len(vehicles),activeTransfers=sum(t.get('status') not in ('completed','cancelled') for t in transfers),
        pendingReports=sum(r.get('status')=='submitted' for r in reports),unread=sum(not n.get('read') for n in mail),
        recentTransfers=[{k:r.get(k,'') for k in ('id','date','time','from','to','status')} for r in recent])

@api.get('/me/summary')
@login_required
def personal_summary():
    uid=g.user['id']
    reports=[r for r in store().list(g.tenant,'reports') if r.get('employeeId')==uid]
    approved=[r for r in reports if r.get('status')=='approved']
    transfers=[r for r in store().list(g.tenant,'transfers') if r.get('employeeId')==uid]
    return jsonify(reports=len(reports),pending=sum(r.get('status')=='submitted' for r in reports),
        activeTasks=sum(r.get('status')!='completed' for r in transfers),
        approvedMinutes=sum(r.get('totals',{}).get('minutes',0) for r in approved),
        earnedCents=sum(r.get('totals',{}).get('laborCents',0)+r.get('totals',{}).get('bonusCents',0) for r in approved),
        expenseCents=sum(r.get('totals',{}).get('expenseCents',0) for r in approved))

@api.errorhandler(400)
@api.errorhandler(401)
@api.errorhandler(403)
@api.errorhandler(404)
@api.errorhandler(409)
def http_error(e):return jsonify(error=e.description),e.code
