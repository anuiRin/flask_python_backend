import config

import pytest, json
import bcrypt
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow = 0)

from app_security import create_app

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api

def setup_function():
    hashed_password = bcrypt.hashpw(b"test", bcrypt.gensalt())
    new_user = {
            'id' : 1,
            'name' : 'test',
            'email' : 'test@test.com',
            'profile' : 'test profile',
            'hashed_password' : hashed_password
    }

    database.execute(text("""
        INSERT INTO users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_user)

def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_tweet(api):
    '''new_user = {
            'email' : 'test6@test.co.kr',
            'password' : 'test',
            'name' : 'mr.test',
            'profile' : 'test profile'
    }

    #sign-up
    resp = api.post(
            '/sign-up',
            data = json.dumps(new_user),
            content_type = 'application/json'
    )
    assert resp.status_code == 200

    resp_json = json.loads(resp.data.decode('utf-8'))
    new_user_id = resp_json['id']
    '''
    #login
    resp = api.post(
            '/login',
            data = json.dumps({'email' : 'test@test.com',
                'password' : 'test'}),
            content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    #tweet
    resp = api.post('/tweet',
            data = json.dumps({'tweet' : "hello api!"}),
            content_type = 'application/json',
            headers = {'Authorization' : access_token}
    )
    assert resp.status_code ==  200

    #check tweet
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
            'user_id' : 1,
            'timeline' : [
                {
                    'user_id' : 1,
                    'tweet' : "hello api!"
                }
            ]
        }

