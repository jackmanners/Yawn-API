import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yapi import YapiClient
from yapi.utilities import epoch

def main():
    yapi = YapiClient()
    
    test_user = {
        'username': 'testuser',
        'password': 'password',
        'email': 'fakeemail@test.com',
        'admin': 0
    }
    
    r = yapi.users.create(test_user)
    
    users = yapi.users.get_all()
    usernames = [user['username'] for user in users.json()]
    
    assert len(usernames) > 0
    assert 'testuser' in usernames
    
    yapi.users.delete('testuser')
    
    users = yapi.users.get_all()
    usernames = [user['username'] for user in users.json()]
    
    assert 'testuser' not in usernames    

if __name__ == '__main__':
    main()