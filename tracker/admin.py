from django.contrib import admin

from .models import Game, Site, League


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "site",
        "league",
        # "game_fee",
        "fee_paid",
        "is_volunteer",
        "mileage",
        "mileage_paid",
        "position",
    )
    search_fields = ("date", "site__name", "league__organization")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name",)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("organization", "assignor", "game_fee")
    search_fields = ("organization", "assignor")
