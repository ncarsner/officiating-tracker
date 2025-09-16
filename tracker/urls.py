"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from tracker import views

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("game/<int:pk>/", views.game_detail, name="game_detail"),
    path("add_game/", views.game_create, name="add_game"),
    path("edit_game/<int:pk>/", views.edit_game, name="edit_game"),
    path("delete_game/<int:pk>/", views.delete_game, name="delete_game"),
    path("site_distance/", views.site_distance, name="site_distance"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
