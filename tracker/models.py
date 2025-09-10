from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Game(models.Model):
    date = models.DateField()
    # Many-to-One: many games can be played at a site
    site = models.ForeignKey("Site", on_delete=models.SET_NULL, null=True)
    # Many-to-One: many games can belong to the same league/organization
    league = models.ForeignKey("League", on_delete=models.SET_NULL, null=True)
    fee_paid = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    mileage = models.FloatField(default=0.0)
    mileage_paid = models.BooleanField(default=False)
    position = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Game on {self.date} at {self.site}"


class Site(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    address = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name


class League(models.Model):
    organization = models.CharField(
        max_length=100, unique=True, blank=False, null=False
    )
    assignor = models.CharField(max_length=100, blank=False, null=False)
    game_fee = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.organization
