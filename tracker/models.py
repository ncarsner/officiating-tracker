from django.db import models


class Game(models.Model):
    date = models.DateField()
    # Many-to-One: many games can be played at a site
    site = models.ForeignKey("Site", related_name="name", on_delete=models.CASCADE)
    # Many-to-One: many games can belong to the same league/organization
    league = models.ForeignKey("League", related_name="organization", on_delete=models.CASCADE)
    # Many-to-One: many games can have the same assignor
    assignor = models.ForeignKey("League", related_name="assignor", on_delete=models.CASCADE)
    # Many-to-One: many games can have the same game fee
    game_fee = models.ForeignKey("League", related_name="game_fee", on_delete=models.CASCADE)

    fee_paid = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    mileage = models.FloatField(default=0.0)
    mileage_paid = models.BooleanField(default=False)
    position = models.CharField(max_length=50, blank=True, null=True)


class Site(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=255, blank=False, null=False)


class League(models.Model):
    organization = models.CharField(max_length=100, blank=False, null=False)
    assignor = models.CharField(max_length=100, blank=False, null=False)
    game_fee = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    description = models.TextField(blank=True)
