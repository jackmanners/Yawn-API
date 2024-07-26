import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yapi import YapiClient as yapi

class TestSnapiClient(unittest.TestCase):
    def test_snapi(self):
        y = yapi()
        self.assertTrue(y.snapi is not None)
        
    def test_users(self):
        y = yapi()
        self.assertTrue(y.users is not None)
        
        test_user = {
            'username': 'testuser',
            'password': 'password',
            'email': 'fakeemail@test.com',
            'admin': 0
        }
        
        r = y.users.create(test_user)
        
        users = y.users.get_all()
        usernames = [user['username'] for user in users.json()]
        
        self.assertTrue(len(usernames) > 0)
        self.assertTrue('testuser' in usernames)
        
        y.users.delete('testuser')
        
        users = y.users.get_all()
        usernames = [user['username'] for user in users.json()]
        
        self.assertTrue('testuser' not in usernames)
        
    def test_participants(self):
        y = yapi()
        self.assertTrue(y.participants is not None)
        
        pxs = y.participants.participant_list()
        self.assertTrue(pxs is not None)
        
        for px in pxs:
            self.assertTrue('lab_id' in px)
            self.assertTrue('study_name' in px)
            
        for px in pxs:
            if px['study_name'] == 'test_study':
                self.assertTrue('lab_id' in px)
                self.assertTrue('study_name' in px)
                break
            else:
                self.fail("No participant in test_study")

if __name__ == '__main__':
    unittest.main()