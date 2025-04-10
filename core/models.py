from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True,null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True,null=True)
    username = models.CharField(max_length=150, unique=True)
    # email = models.EmailField(max_length=255, blank=False, null=False, unique=True)


    def __str__(self):
        return self.username
    
    
    
