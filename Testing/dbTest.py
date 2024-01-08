import unittest
from pymongo import MongoClient
from db import DB


class TestDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = DB()
        cls.client = MongoClient('mongodb://localhost:27017/')
        cls.test_db = cls.client['p2p-chat']

    def setUp(self):
        self.test_db.accounts.delete_many({})
        self.test_db.online_peers.delete_many({})

    def test_is_account_exist(self):
        self.assertFalse(self.db.is_account_exist('testuser'))
        self.test_db.accounts.insert_one({'username': 'testuser', 'password': 'testpass'})
        self.assertTrue(self.db.is_account_exist('testuser'))

    def test_register(self):
        self.db.register('testuser', 'testpass')
        self.assertEqual(self.test_db.accounts.find_one({'username': 'testuser'})['password'], 'testpass')

    def test_get_password(self):
        self.test_db.accounts.insert_one({'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(self.db.get_password('testuser'), 'testpass')

    def test_is_account_online(self):
        self.assertFalse(self.db.is_account_online('testuser'))
        self.test_db.online_peers.insert_one({'username': 'testuser', 'ip': '127.0.0.1', 'port': 5000})
        self.assertTrue(self.db.is_account_online('testuser'))


    def test_get_peer_ip_port(self):
        self.test_db.online_peers.insert_one({'username': 'testuser', 'ip': '127.0.0.1', 'port': 5000})
        self.assertEqual(self.db.get_peer_ip_port('testuser'), ('127.0.0.1', 5000))

    @classmethod
    def tearDownClass(cls):
        cls.test_db.accounts.delete_many({})
        cls.test_db.online_peers.delete_many({})


if __name__ == '__main__':
    unittest.main()
