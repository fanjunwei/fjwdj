import string

from django.contrib.auth.models import User

from django.db import models
from django.utils.crypto import get_random_string

VALID_KEY_CHARS = string.ascii_lowercase + string.digits


class Auth2(models.Model):
    user = models.ForeignKey(User)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=32, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)


def get_new_auth2_token():
    "Returns session key that isn't being used."
    while True:
        token_key = get_random_string(32, VALID_KEY_CHARS)
        if not Auth2.objects.filter(token=token_key).exists():
            break
    return token_key