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
    
    # ============ NEW BUDGET APP ENDPOINTS ============
    # Budget Drafts
    path("budget/draft/add/", views.add_budget_draft),
    path("budget/draft/list/", views.get_budget_drafts),
    path("budget/draft/get_or_create/", views.get_or_create_budget_draft),
    
    # Budget Expenses
    path("budget/expense/add/", views.add_budget_expense),
    path("budget/expense/list/", views.get_budget_expenses),
    path("budget/expense/update/", views.update_budget_expense),
    path("budget/expense/delete/", views.delete_budget_expense),
    path("budget/expense/delete_all/", views.delete_all_budget_expenses),
    
    # Categories
    path("category/list/", views.get_categories),
    path("category/add/", views.add_category),
    path("category/delete/", views.delete_category),
    
    path("budget/draft/delete/", views.delete_budget_draft),
]