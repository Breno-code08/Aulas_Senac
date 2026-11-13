import pytest
from app import create_app
from app.extensions import db
from app.services.catalog import seed_database

@pytest.fixture
def client():
    app = create_app({'TESTING':True,'SECRET_KEY':'test-only-key','SQLALCHEMY_DATABASE_URI':'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
        seed_database()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def send(c, path, method='GET', data=None):
    token = c.get('/api/bootstrap').json['csrf']
    return c.open('/api'+path,method=method,json=data,headers={'X-CSRF-Token':token})

def persona(c, role):
    return send(c,'/session','POST',{'role':role})

def test_flow_and_reports(client):
    c=client
    assert c.post('/api/session',json={'role':'admin'}).status_code==403
    assert c.get('/api/manage').status_code==401
    assert persona(c,'cliente').status_code==200
    assert send(c,'/requests','POST',{'service_id':1,'description':'Trocar tomadas da sala','neighborhood':'Centro','preferred_date':'2099-01-01'}).status_code==200
    r=c.get('/api/bootstrap').json['requests'][0]
    assert send(c,f"/requests/{r['id']}",'PATCH',{'status':'aceita'}).status_code==409
    persona(c,'profissional')
    assert send(c,f"/requests/{r['id']}",'PATCH',{'status':'aceita'}).status_code==200
    assert send(c,f"/requests/{r['id']}/messages",'POST',{'body':'Vamos combinar o horário?'}).status_code==200
    persona(c,'cliente')
    assert len(c.get(f"/api/requests/{r['id']}/messages").json)==1
    assert send(c,f"/requests/{r['id']}",'PATCH',{'status':'concluida'}).status_code==200
    review={'request_id':r['id'],'rating':5,'comment':'Ótima experiência de demonstração.'}
    assert send(c,'/reviews','POST',review).status_code==200
    assert send(c,'/reviews','POST',review).status_code==409
    persona(c,'admin')
    assert len(c.get('/api/reports?status=concluida').json)==3
    assert c.get('/api/reports?format=pdf').data.startswith(b'%PDF')
    assert 'concluida' in c.get('/api/reports?format=csv').text

def test_crud_and_integrity(client):
    c=client
    persona(c,'admin')
    data={'name':'Usuário Teste','email':'teste@example.com','neighborhood':'Centro'}
    assert send(c,'/users','POST',data).status_code==200
    u=c.get('/api/manage').json['users'][-1]
    assert send(c,f"/users/{u['id']}",'PUT',{**data,'name':'Nome editado'}).status_code==200
    assert send(c,f"/users/{u['id']}",'DELETE',{}).status_code==200
    assert send(c,'/categories','POST',{'name':'Jardim'}).status_code==200
    cat=c.get('/api/manage').json['categories'][-1]
    assert send(c,f"/categories/{cat['id']}",'PUT',{'name':'Jardinagem'}).status_code==200
    persona(c,'profissional')
    service={'category_id':cat['id'],'title':'Cuidado de jardim','description':'Cuidados de plantas residenciais.','price':50,'unit':'hora'}
    assert send(c,'/services','POST',service).status_code==200
    s=c.get('/api/manage').json['services'][-1]
    assert send(c,f"/services/{s['id']}",'PUT',{**service,'price':70}).status_code==200
    assert send(c,'/services/2','DELETE',{}).status_code==403
    persona(c,'admin')
    assert send(c,f"/categories/{cat['id']}",'DELETE',{}).status_code==409
    assert send(c,f"/services/{s['id']}",'DELETE',{}).status_code==200
    assert send(c,f"/categories/{cat['id']}",'DELETE',{}).status_code==200
    assert send(c,'/services/1','DELETE',{}).status_code==409

def test_registration_validation_and_favorites(client):
    c=client
    assert send(c,'/register','POST',{'name':'a','email':'bad','role':'admin'}).status_code==400
    data={'name':'Profissional Teste','email':'pro@example.com','role':'profissional','neighborhood':'Centro','profession':'Jardineiro'}
    assert send(c,'/register','POST',data).status_code==200
    assert c.get('/api/manage').json['professional']['profession']=='Jardineiro'
    assert send(c,'/profile','PUT',{'profession':'Jardineiro','bio':'Cuidados com plantas e jardins.','experience':4}).status_code==200
    persona(c,'cliente')
    assert send(c,'/favorites','POST',{'professional_id':1,'saved':True}).status_code==200
    assert c.get('/api/bootstrap').json['favorites']==[1]

def test_separate_registration_pages_and_endpoints(client):
    c=client
    assert c.get('/cadastro/usuario').location.endswith('#cadastro-usuario')
    assert c.get('/cadastro/profissional').location.endswith('#cadastro-profissional')
    base={'name':'Cliente de Teste','email':'cliente.novo@example.com','neighborhood':'Centro','role':'cliente'}
    assert send(c,'/register/users','POST',base).status_code==200
    assert c.get('/api/bootstrap').json['user']['role']=='cliente'
    assert c.get('/api/users').status_code==403
    wrong={**base,'role':'profissional','email':'wrong@example.com','profession':'Pintor'}
    assert send(c,'/register/users','POST',wrong).status_code==400
    professional={**base,'name':'Profissional de Teste','role':'profissional','email':'profissional.novo@example.com'}
    assert send(c,'/register/professionals','POST',professional).status_code==400
    assert send(c,'/register/professionals','POST',{**professional,'profession':'Eletricista residencial'}).status_code==200
    data=c.get('/api/manage').json
    assert data['professional']['profession']=='Eletricista residencial'
    assert data['professional']['user_id']==c.get('/api/bootstrap').json['user']['id']
    assert send(c,'/register/users','POST',{**base,'email':'CLIENTE.NOVO@EXAMPLE.COM'}).status_code==409
    persona(c,'admin')
    records=c.get('/api/users?q=cliente%20de%20teste&role=cliente').json
    assert len(records)==1
    assert c.get('/api/users/'+str(records[0]['id'])).json['email']=='cliente.novo@example.com'

def test_real_server_frontend_and_required_fields(client):
    c=client
    html=c.get('/').text
    assert 'VERSÃO PYTHON' in html
    assert '<script src="/static/js/app.js" defer></script>' in html
    assert 'OFFLINE_SEED' not in html
    js=c.get('/static/js/app.js').text
    assert 'registrationPage(false)' in js and 'registrationPage(true)' in js
    assert 'globalThis.fetch=' not in js and 'localStorage.' not in js
    for key,value in [('name','  '),('email','bad'),('neighborhood','  ')]:
        payload={'name':'Usuário Validação','email':'valid@example.com','neighborhood':'Centro','role':'cliente',key:value}
        assert send(c,'/register/users','POST',payload).status_code==400
