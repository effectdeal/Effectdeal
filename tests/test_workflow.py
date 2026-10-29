import io
import pytest
from app import create_app
from app.domain.calculations import report_totals

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True,'SECRET_KEY':'test-key','DATABASE':str(tmp_path/'data.sqlite'),'APP_MODE':'demo'})

class User:
    def __init__(self, client, role='owner'):
        self.client=client
        self.role(role)
    def role(self,role):
        self.csrf=self.client.get('/api/session').json['csrf']
        r=self.client.post('/api/login',json={'role':role},headers=self.headers)
        assert r.status_code==200,r.json
        self.csrf=r.json['csrf']
        return self
    @property
    def headers(self):return {'X-CSRF-Token':self.csrf}
    def get(self,path):return self.client.get('/api/'+path)
    def post(self,path,data):return self.client.post('/api/'+path,json=data,headers=self.headers)
    def put(self,path,data):return self.client.put('/api/'+path,json=data,headers=self.headers)

def test_shell_and_public_health(app):
    c=app.test_client()
    assert c.get('/').status_code==200
    assert c.get('/api/health').json['status']=='ok'
    assert c.get('/api/reports').status_code==401
    assert c.get('/manifest.webmanifest').status_code==200
    assert c.get('/sw.js').headers['Cache-Control']=='no-store'

def test_csrf_is_required(app):
    c=app.test_client()
    assert c.post('/api/login',json={'role':'owner'}).status_code==403
    u=User(c)
    assert c.post('/api/customers',json={'name':'No token'}).status_code==403

def test_linked_workflow_and_frozen_rate(app):
    u=User(app.test_client())
    e=u.get('employees/driver').json;e['hourlyRate']=200
    assert u.put('employees/driver',e).status_code==200
    u.role('employee')
    t=u.post('transfers/transfer-demo/report',{})
    assert t.json['id']=='report-transfer-demo'
    r=u.get('reports/report-transfer-demo').json
    r['weekendBonus']=100;r['holidayBonus']=50
    r=u.put('reports/'+r['id'],r).json
    assert r['totals']['minutes']==390
    assert r['totals']['totalCents']==187000
    submitted=u.post('reports/'+r['id']+'/action',{'action':'submit','version':r['version']})
    assert submitted.status_code==200,submitted.json
    r=submitted.json
    assert u.post('reports/'+r['id']+'/action',{'action':'approve','version':r['version']}).status_code==403
    u.role('owner')
    assert len(u.get('notifications').json['items'])==1
    e=u.get('employees/driver').json;e['hourlyRate']=350;u.put('employees/driver',e)
    assert u.get('reports/'+r['id']).json['hourlyRate']==200
    approved=u.post('reports/'+r['id']+'/action',{'action':'approve','version':r['version']})
    assert approved.status_code==200,approved.json
    assert approved.json['totals']['totalCents']==187000
    assert u.put('reports/'+r['id'],approved.json).status_code==409
    assert u.post('reports/'+r['id']+'/action',{'action':'approve','version':approved.json['version']}).status_code==409

def test_return_requires_reason_and_allows_edit(app):
    u=User(app.test_client(),'employee');r=u.get('reports/report-transfer-demo').json
    r=u.post('reports/'+r['id']+'/action',{'action':'submit','version':r['version']}).json
    u.role('owner')
    assert u.post('reports/'+r['id']+'/action',{'action':'return','version':r['version']}).status_code==400
    r=u.post('reports/'+r['id']+'/action',{'action':'return','reason':'Doplnit parkování','version':r['version']}).json
    u.role('employee');r['legs'][0]['parking']=50
    response=u.put('reports/'+r['id'],r)
    assert response.status_code==200,response.json
    assert response.json['totals']['expenseCents']==47000

def test_scope_and_dispatcher_restrictions(app):
    u=User(app.test_client(),'employee')
    assert u.get('employees').json['total']==1
    assert u.get('employees/owner').status_code==404
    assert u.get('customers').json['total']==0
    assert u.put('employees/driver',{'version':1,'hourlyRate':900}).status_code==403
    assert u.get('vehicles/transporter').status_code==404
    u.role('dispatcher');v=u.get('vehicles/octavia').json
    v['monthlyPrice']=1
    saved=u.put('vehicles/octavia',v)
    assert saved.status_code==200,saved.json
    assert saved.json['monthlyPrice']==24900
    assert u.post('employees',{'name':'Bad'}).status_code==403

def test_optimistic_concurrency(app):
    u=User(app.test_client());v=u.get('vehicles/octavia').json
    assert u.put('vehicles/octavia',v).status_code==200
    assert u.put('vehicles/octavia',v).status_code==409

def test_demo_sessions_isolated_and_logout_keeps_workspace(app):
    first=User(app.test_client());second=User(app.test_client())
    v=first.get('vehicles/octavia').json;v['model']='Changed';first.put('vehicles/octavia',v)
    assert second.get('vehicles/octavia').json['model']=='Octavia'
    assert first.post('logout',{}).status_code==200
    first.role('employee')
    assert first.get('vehicles/octavia').json['model']=='Changed'

def test_attachment_protected_and_metadata_only(app):
    u=User(app.test_client(),'employee')
    response=u.client.post('/api/documents/upload',data={'parentKind':'reports','parentId':'report-transfer-demo','file':(io.BytesIO(b'%PDF-1.7\ntest'),'ticket.pdf')},headers=u.headers)
    assert response.status_code==201,response.json
    d=response.json
    assert 'content' not in d
    assert u.get('documents/'+d['id']+'/file').data.startswith(b'%PDF-')
    assert 'content' not in u.get('documents').json['items'][0]
    other=User(app.test_client())
    assert other.get('documents/'+d['id']+'/file').status_code==404

def test_invalid_attachment(app):
    u=User(app.test_client(),'employee')
    r=u.client.post('/api/documents/upload',data={'parentKind':'reports','parentId':'report-transfer-demo','file':(io.BytesIO(b'<script>bad</script>'),'fake.png')},headers=u.headers)
    assert r.status_code==400

def test_calculation_breaks_and_rounding():
    r={'legs':[{'minutes':105,'breakMinutes':15,'tickets':'420.50'}],'weekendBonus':'50.20','holidayBonus':0,'reward':0,'overtimeMinutes':30}
    result=report_totals(r,'200.25')
    assert result=={'minutes':90,'overtimeMinutes':30,'laborCents':30038,'expenseCents':42050,'bonusCents':5020,'totalCents':77108}
    with pytest.raises(ValueError):report_totals({'legs':[{'minutes':10,'breakMinutes':20}]},0)
    with pytest.raises(ValueError):report_totals({'legs':[{'minutes':-1}]},0)

def test_new_transfer_creates_only_one_report(app):
    u=User(app.test_client());t=u.post('transfers',{'employeeId':'driver','vehicleId':'octavia','from':'Praha','to':'Brno','date':'2026-10-29'}).json
    a=u.post('transfers/'+t['id']+'/report',{});b=u.post('transfers/'+t['id']+'/report',{})
    assert a.status_code==201,a.json
    assert a.json['id']==b.json['id']
    assert u.get('reports').json['total']==2
