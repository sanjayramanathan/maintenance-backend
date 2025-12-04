from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.admin_login),
    path("viewer/", views.viewer_login),

    # owner
    path("owner/add/", views.add_owner),
    path("owner/list/", views.get_owners),

    # expense
    path("expense/add/", views.add_expense),
    path("expense/list/", views.get_expenses),
]
