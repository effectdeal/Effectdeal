import base64
import io
import pytest
from app import create_app

PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aKp8AAAAASUVORK5CYII=')

@pytest.fixture
def user(tmp_path):
    application=create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':str(tmp_path/'photos.sqlite'),'APP_MODE':'demo'})
    client=application.test_client()
    token=client.get('/api/session').json['csrf']
    login=client.post('/api/login',json={'role':'owner'},headers={'X-CSRF-Token':token})
    return client,{'X-CSRF-Token':login.json['csrf']}

def upload(user,vehicle='octavia'):
    client,headers=user
    r=client.post('/api/documents/upload',data={'parentKind':'vehicles','parentId':vehicle,'file':(io.BytesIO(PNG),'auto.png')},headers=headers)
    assert r.status_code==201,r.json
    return r.json

def test_first_photo_becomes_cover_and_can_be_changed(user):
    client,headers=user
    first=upload(user);second=upload(user)
    vehicle=client.get('/api/vehicles/octavia').json
    assert vehicle['profileDocumentId']==first['id']
    updated=client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'profileDocumentId':second['id']},headers=headers)
    assert updated.status_code==200,updated.json
    assert updated.json['profileDocumentId']==second['id']
    assert updated.json['monthlyPrice']==24900
    third=upload(user)
    assert client.get('/api/vehicles/octavia').json['profileDocumentId']==second['id']

def test_images_open_inline_and_explicit_download_still_works(user):
    client,_=user
    photo=upload(user)
    view=client.get('/api/documents/'+photo['id']+'/file')
    assert view.status_code==200
    assert view.mimetype=='image/png'
    assert view.headers['Content-Disposition'].startswith('inline')
    assert view.headers['Cache-Control']=='no-store'
    assert view.data==PNG
    download=client.get('/api/documents/'+photo['id']+'/file?download=1')
    assert download.headers['Content-Disposition'].startswith('attachment')

def test_cover_must_belong_to_same_vehicle(user):
    client,headers=user
    photo=upload(user,'transporter')
    vehicle=client.get('/api/vehicles/octavia').json
    response=client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'profileDocumentId':photo['id']},headers=headers)
    assert response.status_code==400
    assert not client.get('/api/vehicles/octavia').json.get('profileDocumentId')

def test_employee_can_view_assigned_photo_but_cannot_set_cover(user):
    client,headers=user
    photo=upload(user);other=upload(user,'transporter')
    result=client.post('/api/login',json={'role':'employee'},headers=headers)
    headers={'X-CSRF-Token':result.json['csrf']}
    assert client.get('/api/documents/'+photo['id']+'/file').status_code==200
    assert client.get('/api/documents/'+other['id']+'/file').status_code==404
    vehicle=client.get('/api/vehicles/octavia').json
    assert client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'profileDocumentId':photo['id']},headers=headers).status_code==403

def test_parent_filter_does_not_truncate_images_from_other_vehicles(user):
    client,_=user
    first=upload(user);upload(user,'transporter')
    result=client.get('/api/documents?parentKind=vehicles&parentId=octavia&limit=1').json
    assert result['total']==1
    assert [r['id'] for r in result['items']]==[first['id']]
    assert 'content' not in result['items'][0]

def test_photo_limit_remains_ten(user):
    client,headers=user
    for _ in range(10):upload(user)
    response=client.post('/api/documents/upload',data={'parentKind':'vehicles','parentId':'octavia','file':(io.BytesIO(PNG),'eleventh.png')},headers=headers)
    assert response.status_code==400

def test_pdf_is_not_a_cover_and_remains_a_download(user):
    client,headers=user
    response=client.post('/api/documents/upload',data={'parentKind':'reports','parentId':'report-transfer-demo','file':(io.BytesIO(b'%PDF-1.7\ntest'),'ticket.pdf')},headers=headers)
    assert response.status_code==201
    doc=response.json
    assert client.get('/api/documents/'+doc['id']+'/file').headers['Content-Disposition'].startswith('attachment')
    vehicle=client.get('/api/vehicles/octavia').json
    assert client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'profileDocumentId':doc['id']},headers=headers).status_code==400

def test_stale_cover_selection_does_not_overwrite_newer_vehicle(user):
    client,headers=user
    photo=upload(user)
    vehicle=client.get('/api/vehicles/octavia').json
    assert client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'color':'Červená'},headers=headers).status_code==200
    response=client.put('/api/vehicles/octavia',json={'version':vehicle['version'],'profileDocumentId':photo['id']},headers=headers)
    assert response.status_code==409
