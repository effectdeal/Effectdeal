from datetime import date,timedelta
from test_workflow import app,User


def test_unavailability_requires_dates_and_expires(app):
    u=User(app.test_client());v=u.get('vehicles/transporter').json
    assert u.put('vehicles/transporter',{'version':v['version'],'status':'unavailable'}).status_code==400
    assert u.put('vehicles/transporter',{'version':v['version'],'status':'unavailable','unavailableFrom':'2030-05-20','unavailableTo':'2030-05-01'}).status_code==400
    r=u.put('vehicles/transporter',{'version':v['version'],'status':'unavailable','unavailableFrom':'2020-01-01','unavailableTo':'2020-01-02'})
    assert r.status_code==200,r.json
    assert r.json['status']=='available' and r.json['baseStatus']=='unavailable'
    assert r.json['unavailableFrom']=='2020-01-01'


def test_conflicting_assignment_is_rejected(app):
    u=User(app.test_client());v=u.get('vehicles/transporter').json
    day=date.today().isoformat()
    r=u.put('vehicles/transporter',{'version':v['version'],'status':'unavailable','unavailableFrom':day,'unavailableTo':day})
    assert r.status_code==200,r.json
    assert r.json['status']=='unavailable'
    assert u.post('transfers',{'vehicleId':v['id'],'employeeId':'driver','from':'Praha','to':'Brno','date':day}).status_code==400
    assert u.post('rentals',{'vehicleId':v['id'],'customerId':'customer-demo','start':day,'end':(date.today()+timedelta(days=30)).isoformat()}).status_code==400


def test_driver_progress_updates_derived_vehicle_and_location(app):
    u=User(app.test_client());task=u.get('transfers/transfer-demo').json
    u.role('employee')
    assert u.post('transfers/transfer-demo/status',{'version':task['version'],'status':'progress'}).status_code==200
    vehicle=u.get('vehicles/octavia').json
    assert vehicle['status']=='delivering'
    assert 'monthlyPrice' not in vehicle
    task=u.get('transfers/transfer-demo').json
    assert u.post('transfers/transfer-demo/status',{'version':task['version'],'status':'cancelled'}).status_code==403
    assert u.post('transfers/transfer-demo/status',{'version':task['version'],'status':'completed'}).status_code==200
    vehicle=u.get('vehicles/octavia').json
    assert vehicle['status']!='delivering'
    assert vehicle['location']==task['to']
    assert u.post('transfers/transfer-demo/status',{'version':task['version'],'status':'completed'}).status_code==409
    u.role('owner')
    v=u.get('vehicles/octavia').json
    updated=u.put('vehicles/octavia',{'version':v['version'],'location':'Liberec'})
    assert updated.json['location']=='Liberec'


def test_status_changes_cannot_target_other_employee_task(app):
    u=User(app.test_client());v=u.get('vehicles/transporter').json
    task=u.post('transfers',{'vehicleId':v['id'],'employeeId':'owner','from':'Praha','to':'Brno'}).json
    u.role('employee')
    assert u.post('transfers/'+task['id']+'/status',{'version':1,'status':'progress'}).status_code==404
    assert u.get('dashboard').status_code==403


def test_documents_queries_are_bounded_and_filtered(app,monkeypatch):
    u=User(app.test_client());catalog=u.get('catalog/effectdeal').json
    for item in catalog['items'][:3]:u.post('catalog/effectdeal/'+item['sourceSlug']+'/import',{})
    backing=app.extensions['store'];original=backing.get;calls=[]
    def counted(*args):calls.append(args);return original(*args)
    monkeypatch.setattr(backing,'get',counted)
    target=catalog['items'][0]
    result=u.get('documents?parentKind=vehicles&parentId='+target['id'])
    assert result.status_code==200
    assert len(result.json['items'])==target['photoCount']
    assert len(calls)<=2  # one authenticated user, one parent, not one query per photo


def test_thumbnail_small_and_access_checked_even_with_etag(app):
    u=User(app.test_client());item=u.get('catalog/effectdeal').json['items'][0]
    u.post('catalog/effectdeal/'+item['sourceSlug']+'/import',{})
    vehicle=u.get('vehicles/'+item['id']).json
    path='documents/'+vehicle['profileDocumentId']+'/file?size=thumb'
    response=u.get(path)
    assert response.status_code==200 and response.mimetype=='image/webp'
    assert len(response.data)<100_000
    assert response.headers['Cache-Control']=='private, no-cache'
    etag=response.headers['ETag']
    assert u.client.get('/api/'+path,headers={'If-None-Match':etag}).status_code==304
    u.role('employee')
    assert u.client.get('/api/'+path,headers={'If-None-Match':etag}).status_code==404
