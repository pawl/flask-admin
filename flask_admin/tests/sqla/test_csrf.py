import os
import wtforms

from nose.tools import eq_, ok_

if int(wtforms.__version__[0]) < 2:
    from nose.plugins.skip import SkipTest
    raise SkipTest('CSRF is not available in WTForms <2.')

from wtforms.form import Form
from wtforms.csrf.session import SessionCSRF
from wtforms.meta import DefaultMeta

from flask import session
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import form

from . import setup

from datetime import timedelta

app, db, admin = setup()
client = app.test_client()


# Set up models and database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


db.create_all()


# Create Base Form w/ CSRF
class SecureForm(form.BaseForm):
    class Meta(DefaultMeta):
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = os.urandom(24)
        csrf_time_limit = timedelta(minutes=20)
        
        @property
        def csrf_context(self):
            return session


class SecureModelView(ModelView):
    form_base_class = SecureForm


view = SecureModelView(User, db.session)
admin.add_view(view)


def get_csrf_token(data):
    data = data.split('name="csrf_token" type="hidden" value="')[1]
    token = data.split('">')[0]
    return token


def test_create_view():
    rv = client.get('/admin/user/new/')
    eq_(rv.status_code, 200)
    ok_(u'name="csrf_token"' in rv.data.decode('utf-8'))
    
    csrf_token = get_csrf_token(rv.data.decode('utf-8'))
    
    # Submit create_view without CSRF token
    rv = client.post('/admin/user/new/', data=dict(name='test1'))
    eq_(rv.status_code, 200)
    
    # Submit create_view with CSRF token
    rv = client.post('/admin/user/new/', data=dict(name='test1',
                                                   csrf_token=csrf_token))
    eq_(rv.status_code, 302)


def test_edit_view():
    rv = client.get('/admin/user/edit/?url=%2Fadmin%2Fuser%2F&id=1')
    eq_(rv.status_code, 200)
    ok_(u'name="csrf_token"' in rv.data.decode('utf-8'))
    
    csrf_token = get_csrf_token(rv.data.decode('utf-8'))
    
    # Submit edit_view without CSRF token
    rv = client.post('/admin/user/edit/?url=%2Fadmin%2Fuser%2F&id=1', 
                     data=dict(name='test1'))
    eq_(rv.status_code, 200)
    
    # Submit edit_view with CSRF token
    rv = client.post('/admin/user/edit/?url=%2Fadmin%2Fuser%2F&id=1',
                     data=dict(name='test1', csrf_token=csrf_token))
    eq_(rv.status_code, 302)


def test_delete():
    rv = client.get('/admin/user/')
    eq_(rv.status_code, 200)
    ok_(u'name="csrf_token"' in rv.data.decode('utf-8'))
    
    csrf_token = get_csrf_token(rv.data.decode('utf-8'))
    
    # Delete without CSRF token
    rv = client.post('/admin/user/delete/?url=%2Fadmin%2Fuser%2F&id=1', 
                     data=dict(name='test1'))
    eq_(rv.status_code, 200)
    
    # Delete with CSRF token
    rv = client.post('/admin/user/delete/?url=%2Fadmin%2Fuser%2F&id=1',
                     data=dict(name='test1', csrf_token=csrf_token))
    eq_(rv.status_code, 302)
