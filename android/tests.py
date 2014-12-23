import datetime
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from android.auth2 import getAuth2Token, checkAuth2Token


class ViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('fanjunwei', 'fanjunwei@17.com', '123')

    def test1(self):
        token = getAuth2Token(self.user)
        token2 = getAuth2Token(self.user)
        self.assertEqual(token, token2)

        check_user = checkAuth2Token(token)
        self.assertEquals(check_user, self.user)

        check_user = checkAuth2Token('12323dfdfdf')
        self.assertEquals(check_user, None)

        self.user.set_password('22df')
        self.user.save()
        check_user = checkAuth2Token(token)
        self.assertEquals(check_user, None)
        token3 = getAuth2Token(self.user)
        self.assertNotEqual(token, token3)

    def test2(self):
        token = getAuth2Token(self.user)
        check_user = checkAuth2Token(token, datetime.datetime(2015, 3, 1))
        self.assertEquals(check_user, None)

        token_timeout = getAuth2Token(self.user, datetime.datetime(2015, 3, 1))
        self.assertNotEquals(token, token_timeout)

        check_user = checkAuth2Token(token_timeout, datetime.datetime(2015, 3, 1))
        self.assertEquals(check_user, self.user)
