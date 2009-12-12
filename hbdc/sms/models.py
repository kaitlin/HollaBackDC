from django.db import models

# Create your models here.

class SMS(models.Model):

    phone_number = models.CharField(max_length=12)

    message = models.CharField(max_length=160, null=True, blank=True)	

    timestamp = models.DateTimeField()

