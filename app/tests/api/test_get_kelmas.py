import app.tests.helpers as helpers

def test_get_kelmas(app, client):
    with app.app_context():
        start = 0
        size = 100
        page = 0
        
        kelmas = helpers.create_random_kelmas(200)
        
        resp = client.get(f"/api/kelmas?start={start}&page={page}&size={size}")
        json = resp.json
        assert resp.status_code >= 200 and resp.status_code < 300
        assert len(json) == size
        assert json[0]['sort'] == 1
        x={}
        resp = client.get(f"/api/kelmas?start={start}&page={page+1}&size={size}")
        json = resp.json
        assert resp.status_code >= 200 and resp.status_code < 300
        assert len(json) == size
        assert json[0]['sort'] == size+1
        keys = ['sort', 'display_name', 'image_url', 'id', 'content', 'username', 'premium']
        assert all((key in json[0]) for key in keys)
        for key in keys:
            json[0].pop(key)
        assert json[0] == {}
        

def test_get_kelmas_with_empty_db(app, client):
    with app.app_context():
        start = 0
        size = 100
        page = 0
        
        resp = client.get(f"/api/kelmas?start={start}&page={page}&size={size}")
        assert resp.status_code >= 200 and resp.status_code < 300
        assert len(resp.json) == 0    

def test_get_kelmas_with_invalid_start(app, client):
    with app.app_context():
        start = -1
        size = 100
        page = 0
        
        kelmas = helpers.create_random_kelmas(200)
        
        resp = client.get(f"/api/kelmas?start={start}&page={page}&size={size}")
        assert resp.status_code >= 400
        
def test_get_kelmas_with_invalid_size(app, client):
    with app.app_context():
        start = 0
        size = -1
        page = 0
        
        kelmas = helpers.create_random_kelmas(200)
        
        resp = client.get(f"/api/kelmas?start={start}&page={page}&size={size}")
        assert resp.status_code >= 400