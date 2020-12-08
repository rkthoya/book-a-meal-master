import json
import unittest
from app import create_app, db
from app.models import MenuType
from tests.base import BaseTest


class MenuTestCase(BaseTest):
    """ This will test menu resource endpoints"""

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client
        self.headers = {'Content-Type' : 'application/json'} 
        self.menu = json.dumps({
            'category': MenuType.BREAKFAST
        })

        with self.app.app_context():
            db.create_all()

    def test_menu_creation(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        json_result = json.loads(res.get_data(as_text=True))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(json_result['category'], MenuType.BREAKFAST)

    def test_cannot_create_menu_without_category(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=json.dumps({}),
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 400)

    def test_cannot_create_menu_with_non_existing_category(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=json.dumps({'category': 40}),
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 400)

    def test_can_get_all_menus(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        json_result = json.loads(res.get_data(as_text=True))
        self.assertEqual(res.status_code, 201)
        customer_header, _ = self.loginCustomer()
        res = self.client().get('/api/v1/menu', headers=customer_header)

        json_result = json.loads(res.get_data(as_text=True))
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'objects', res.data)

    def test_can_get_menu_by_id(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 201)

        customer_header, _ = self.loginCustomer()
        json_result = json.loads(res.get_data(as_text=True))
        res = self.client().get(
            '/api/v1/menu/{}'.format(json_result['id']),
            headers=customer_header
        )

        json_result = json.loads(res.get_data(as_text=True))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_result['category'], MenuType.BREAKFAST)

    def test_menu_can_be_updated(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 201)

        res = self.client().put(
            '/api/v1/menu/1',
            data=json.dumps({
                'category': MenuType.SUPPER
            }),
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 200)

        customer_header, _ = self.loginCustomer()
        res = self.client().get('/api/v1/menu/1', headers=customer_header)
        json_result = json.loads(res.get_data(as_text=True))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_result['category'], MenuType.SUPPER)

    def test_cannot_update_menu_without_category(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 201)

        res = self.client().put(
            '/api/v1/menu/1',
            data=json.dumps({}),
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 400)

    def test_cannot_update_menu_with_non_existing_category(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 201)

        res = self.client().put(
            '/api/v1/menu/1',
            data=json.dumps({'category': 50}),
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 400)

    def test_menu_deletion(self):
        caterer_header, _ = self.loginCaterer()
        res = self.client().post(
            '/api/v1/menu',
            data=self.menu,
            headers=caterer_header
        )
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/api/v1/menu/1',
                                   headers=caterer_header)
        self.assertEqual(res.status_code, 200)
        customer_header, _ = self.loginCustomer()
        res = self.client().get('/api/v1/menu/1', headers=customer_header)
        self.assertEqual(res.status_code, 404)
