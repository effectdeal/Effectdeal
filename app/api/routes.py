import base64
import functools
import secrets
from datetime import datetime, timezone
from uuid import uuid4
from flask import Blueprint, current_app, g, jsonify, request, session, abort, Response
from werkzeug.security import check_password_hash, generate_password_hash
from ..domain.calculations import number, report_totals
from ..domain.seeds import seed
from ..storage import Conflict

api=Blueprint('api',__name__)
KINDS={'employees','vehicles','customers','rentals','transfers','reports','notifications','handover','documents','service','invoices','payments'}
ROLES={'owner','manager','dispatcher','employee'}
STAFF={'owner','manager','dispatcher'}
def store(): return current_app.extensions['store']
def now(): return datetime.now(timezone.utc).isoformat()
def public(record): return {k:v for k,v in record.items() if k not in ('passwordHash','content')}
def csrf():
    if request.method not in ('GET','HEAD','OPTIONS') and (not session.get('csrf') or request.headers.get('X-CSRF-Token')!=session.get('csrf')):
        abort(403,description='Obnovte stránku a zkuste to znovu.')
def login_required(fn):
    @functools.wraps(fn)
    def wrapped(*args,**kwargs):
        if not session.get('user'): abort(401,description='Přihlaste se prosím.')
        g.tenant=session['tenant'];g.user=store().get(g.tenant,'employees',session['user'])
        if not g.user or g.user.get('disabled'): abort(401)
        csrf();return fn(*args,**kwargs)
    return wrapped

def scoped(kind,r):
    role=g.user['role'];uid=g.user['id']
    if kind=='notifications': return r.get('recipient') in (uid,role)
    if kind in ('invoices','payments') and role not in ('owner','manager'):return False
    if role in STAFF: return True
    if kind=='employees': return r['id']==uid
    if kind in ('reports','transfers','handover'): return r.get('employeeId')==uid
    if kind=='vehicles': return any(t.get('employeeId')==uid and t.get('vehicleId')==r['id'] for t in store().list(g.tenant,'transfers'))
    if kind=='documents':
        parent=store().get(g.tenant,r.get('parentKind',''),r.get('parentId',''))
        return parent is not None and scoped(r['parentKind'],parent)
    return False

def get_record(kind,id):
    if kind not in KINDS: abort(404)
    r=store().get(g.tenant,kind,id)
    if not r or not scoped(kind,r): abort(404)
    return r

def writable(kind,r=None):
    role=g.user['role']
    if r and not scoped(kind,r): abort(404)
    if kind in ('notifications','documents'): abort(403)
    if kind=='employees':
        if role not in ('owner','manager'): abort(403)
        if r and r.get('role')=='owner' and role!='owner': abort(403)
    elif kind in ('invoices','payments'):
        if role not in ('owner','manager'): abort(403)
    elif kind in ('reports','handover'):
        if r and kind=='reports' and r['status'] not in ('draft','returned'): abort(409,description='Odeslaný výkaz lze pouze schválit, zamítnout nebo vrátit.')
    elif role not in STAFF: abort(403)

FIELDS={
 'employees':{'name','email','role','hourlyRate','available','latitude','longitude','locationConfirmedAt','disabled','password'},
 'vehicles':{'brand','model','plate','vin','year','color','drive','fuel','transmission','power','equipment','description','status','monthlyPrice','location','latitude','longitude','odometer','defects','lastRentalEnd','profileDocumentId'},
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
    for k in NUMERIC & r.keys():r[k]=float(number(r[k]))
    for k,v in r.items():
        if isinstance(v,str) and len(v)>10000 and k!='signature':raise ValueError('Text je příliš dlouhý.')
    role=g.user['role']
    if kind=='employees':
        if r.get('role','employee') not in ROLES:raise ValueError('Neplatná role.')
        if role!='owner' and r.get('role')=='owner':abort(403)
        if old and old.get('role')=='owner':r['role']='owner';r['disabled']=False
        r.setdefault('hourlyRate',0);r.setdefault('role','employee');r['available']=r.get('available',True) in (True,'true','True')
        if not r.get('name') or '@' not in r.get('email',''):raise ValueError('Vyplňte jméno a e-mail.')
        r['email']=r['email'].strip().lower()
        if any(e['email']==r['email'] and e['id']!=r.get('id') for e in store().list(g.tenant,'employees')):raise ValueError('E-mail již existuje.')
        password=r.pop('password',None)
        if password:
            if len(password)<12:raise ValueError('Heslo musí mít alespoň 12 znaků.')
            r['passwordHash']=generate_password_hash(password)
        if not old and current_app.config['APP_MODE']=='production' and not password:raise ValueError('Nový účet vyžaduje heslo.')
    if kind in ('vehicles','rentals') and role=='dispatcher':
        r['monthlyPrice']=(old or {}).get('monthlyPrice',0)
    if kind=='vehicles':
        for key in ('brand','model','plate'):
            if not str(r.get(key,'')).strip():raise ValueError('Vyplňte značku, model a SPZ.')
        r.setdefault('status','available');r.setdefault('monthlyPrice',0)
    for key,target in [('employeeId','employees'),('vehicleId','vehicles'),('customerId','customers'),('rentalId','rentals'),('transferId','transfers')]:
        if r.get(key) and not store().get(g.tenant,target,r[key]):raise ValueError('Navázaný záznam neexistuje: '+key)
    if kind=='rentals':
        if not r.get('customerId') or not r.get('vehicleId'):raise ValueError('Vyberte zákazníka a vozidlo.')
        if not r.get('start') or not r.get('end') or r['end']<=r['start']:raise ValueError('Konec pronájmu musí být po začátku.')
        r.setdefault('status','reserved')
    if kind=='transfers':
        if not r.get('vehicleId') or not r.get('employeeId') or not r.get('from') or not r.get('to'):raise ValueError('Vyplňte vozidlo, zaměstnance a trasu.')
        rental=store().get(g.tenant,'rentals',r.get('rentalId',''))
        if rental:r['customerId']=rental['customerId'];r['vehicleId']=rental['vehicleId']
        r.setdefault('status','assigned')
        if old and old.get('reportId') and any(r.get(k)!=old.get(k) for k in ('employeeId','vehicleId','rentalId')):raise ValueError('Převoz již má výkaz. Přiřazení již nelze měnit.')
    if kind=='reports':
        if r.get('transferId'):
            transfer=store().get(g.tenant,'transfers',r['transferId'])
            if not scoped('transfers',transfer):abort(404)
            r['employeeId']=transfer['employeeId'];r['vehicleId']=transfer['vehicleId']
        if role not in STAFF:r['employeeId']=g.user['id']
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
def health():return jsonify(status='ok',app='EFFECT DEAL',version='0.1.0')
@api.get('/session')
def session_info():
    session.setdefault('csrf',secrets.token_hex(24))
    user=store().get(session.get('tenant',''), 'employees',session.get('user',''))
    return jsonify(user=public(user) if user else None,csrf=session['csrf'],mode=current_app.config['APP_MODE'])
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
        u=next((u for u in users if u.get('email')==str(p.get('email','')).strip().lower()),None)
        if not u or u.get('disabled') or not check_password_hash(u.get('passwordHash',''),p.get('password','')):abort(401,description='Neplatné přihlašovací údaje.')
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
    rows=[public(r) for r in store().list(g.tenant,kind) if scoped(kind,r)]
    search=request.args.get('q','').lower();status=request.args.get('status');employee=request.args.get('employeeId')
    rows=[r for r in rows if (not search or search in str(r).lower()) and (not status or r.get('status')==status) and (not employee or r.get('employeeId')==employee)]
    rows.sort(key=lambda r:r.get('updatedAt',r.get('createdAt','')),reverse=True)
    limit=min(max(int(request.args.get('limit',50)),1),100);offset=max(int(request.args.get('offset',0)),0)
    return jsonify(items=rows[offset:offset+limit],total=len(rows))
@api.get('/<kind>/<id>')
@login_required
def detail(kind,id):return jsonify(public(get_record(kind,id)))
@api.post('/<kind>')
@login_required
def create(kind):
    if kind not in FIELDS:abort(404)
    writable(kind);p=request.get_json() or {};r=validate(kind,p);r.update(id=uuid4().hex,createdAt=now(),updatedAt=now())
    r=store().create(g.tenant,kind,r)
    return jsonify(public(r)),201
@api.put('/<kind>/<id>')
@login_required
def update(kind,id):
    if kind not in FIELDS:abort(404)
    old=get_record(kind,id);writable(kind,old);p=request.get_json() or {}
    if p.get('version')!=old['version']:raise Conflict('Záznam je zastaralý. Obnovte ho.')
    r=validate(kind,p,old);r['updatedAt']=now();r=store().update(g.tenant,kind,r,old['version'])
    return jsonify(public(r))
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
    if kind not in ('reports','vehicles','handover','rentals'):abort(400)
    parent=get_record(kind,id)
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
    count=sum(d.get('parentKind')==kind and d.get('parentId')==id for d in store().list(g.tenant,'documents'))
    if count>=10:raise ValueError('Nejvýše 10 příloh na záznam.')
    # Files stay behind authenticated API; Mongo document is capped below 16 MB.
    r=store().create(g.tenant,'documents',{'id':uuid4().hex,'parentKind':kind,'parentId':id,'name':f.filename[:150],'mime':mime,'size':len(content),'createdAt':now(),'content':base64.b64encode(content).decode()})
    return jsonify(public(r)),201
@api.get('/documents/<id>/file')
@login_required
def document_file(id):
    r=get_record('documents',id)
    return Response(base64.b64decode(r['content']),mimetype=r['mime'],headers={'Content-Disposition':"attachment; filename=document"})

@api.errorhandler(400)
@api.errorhandler(401)
@api.errorhandler(403)
@api.errorhandler(404)
@api.errorhandler(409)
def http_error(e):return jsonify(error=e.description),e.code
