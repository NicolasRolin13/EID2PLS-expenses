from django.test import TestCase, Client
from expenses.models import Atom, Bill, ExtendedUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse

class OneUserTestCase(TestCase):
    user_properties = {
                       'username': 'testuser',
                       'first_name': 'Jane',
                       'last_name': 'Doe',
                       'email': 'jane.doe@null.null',
                       'is_superuser': True,
                      }
    user_password = 'password'
    extendeduser_properties = {
                               'nickname': 'jane_doe',
                              }

    def __init__(self, *args, **kwargs):
        testuser = None
        super().__init__(*args, **kwargs)

    def setUp(self):
        hash_pass = make_password(self.user_password)
        User.objects.create(password=hash_pass, **self.user_properties)
        self.testuser = User.objects.get(username=self.user_properties['username'])
        ExtendedUser.objects.create(user=self.testuser, **self.extendeduser_properties)

    def tearDown(self):
        self.testuser.delete()

    def test_login(self):
        client = Client()
        username = self.user_properties['username']
        password = self.user_password
        response = client.post(reverse('login'), {'username': username, 'password':password})
        self.assertEqual(response.status_code, 302)
