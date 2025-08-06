from django.db import models

# Create your models here.

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    site = models.CharField(max_length=100, blank=False)
    league = models.CharField(max_length=100, blank=False)
    # db_handler = models.ForeignKey("DatabaseHandler", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    assignor = models.CharField(max_length=100, blank=False)
    game_fee = models.PositiveIntegerField(max_length=10, blank=False)
    fee_paid = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    mileage = models.FloatField(default=0.0)
    mileage_paid = models.BooleanField(default=False)
    position = models.CharField(max_length=50, blank=True)

class Site(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=255, blank=False)
    # city = models.CharField(max_length=100, blank=False)
    # state = models.CharField(max_length=50, blank=False)
    # zip_code = models.CharField(max_length=10, blank=False)

class League(models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=100, blank=False)
    contact_person = models.CharField(max_length=100, blank=False)
    # name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
