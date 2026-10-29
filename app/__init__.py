import os
import secrets
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from werkzeug.security import generate_password_hash
from .storage import SQLiteStore, MongoStore, Conflict

def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY') or secrets.token_hex(32), APP_MODE=os.getenv('APP_MODE','demo'),
      DATABASE=os.getenv('DATABASE','/tmp/effectdeal-demo.sqlite'), MAX_CONTENT_LENGTH=11*1024*1024,
      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('APP_MODE')=='production',
      SEND_FILE_MAX_AGE_DEFAULT=0)
    if config: app.config.update(config)
    if app.config['APP_MODE']=='production':
        if len(os.getenv('SECRET_KEY',''))<32 or not os.getenv('MONGODB_URI'):
            raise RuntimeError('Production requires a persistent SECRET_KEY and MONGODB_URI.')
        store=MongoStore(os.environ['MONGODB_URI'],os.getenv('MONGODB_DATABASE','effectdeal'))
        if not store.get('company','employees','owner'):
            email,password=os.getenv('OWNER_EMAIL',''),os.getenv('OWNER_PASSWORD','')
            if not email or len(password)<12: raise RuntimeError('Configure OWNER_EMAIL and OWNER_PASSWORD (12+ chars).')
            store.create('company','employees',{'id':'owner','name':'Majitel','email':email.lower(),'role':'owner','hourlyRate':0,'available':True,'passwordHash':generate_password_hash(password)})
    else:
        store=SQLiteStore(app.config['DATABASE'])
    app.extensions['store']=store
    from .api.routes import api
    app.register_blueprint(api,url_prefix='/api')
    @app.get('/')
    def index(): return render_template('index.html')
    @app.get('/sw.js')
    def worker(): return app.send_static_file('sw.js')
    @app.get('/manifest.webmanifest')
    def manifest(): return app.send_static_file('manifest.webmanifest')
    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        if request.path.startswith('/api/') or request.path in ('/','/sw.js','/manifest.webmanifest'):
            response.headers['Cache-Control']='no-store'
        else:
            response.headers['Cache-Control']='public, max-age=0, must-revalidate'
        return response
    @app.errorhandler(ValueError)
    def invalid(e): return jsonify(error=str(e)),400
    @app.errorhandler(Conflict)
    def conflict(e): return jsonify(error=str(e)),409
    @app.errorhandler(413)
    def too_large(e): return jsonify(error='Soubor je příliš velký (maximum 10 MB).'),413
    return app
