from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AdminUser, HouseOwner, Expense
from .serializers import AdminSerializer, OwnerSerializer, ExpenseSerializer
import hashlib
from .models import BudgetDraft, BudgetExpense, Category
from .serializers import BudgetDraftSerializer, BudgetExpenseSerializer, CategorySerializer


# ---------------------------
# Register Admin
# ---------------------------
@api_view(["POST"])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "All fields required"})

    if AdminUser.objects.filter(username=username).exists():
        return Response({"error": "Username exists"})

    if AdminUser.objects.filter(email=email).exists():
        return Response({"error": "Email exists"})

    # enforce unique password
    pass_sha = hashlib.sha256(("unique" + password).encode()).hexdigest()
    if AdminUser.objects.filter(password_sha256=pass_sha).exists():
        return Response({"error": "Password already used by another admin"})

    admin = AdminUser(username=username, email=email)
    admin.set_password(password)
    admin.save()

    return Response({"success": True, "admin_id": admin.id})


# ---------------------------
# Admin Login
# ---------------------------
@api_view(["POST"])
def admin_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    try:
        admin = AdminUser.objects.get(username=username)
    except:
        return Response({"error": "Invalid credentials"})

    if not admin.check_password(password):
        return Response({"error": "Invalid credentials"})

    return Response({"success": True, "admin_id": admin.id})


# ---------------------------
# Viewer Login
# viewer enters admin password
# ---------------------------
@api_view(["POST"])
def viewer_login(request):
    password = request.data.get("password")
    if not password:
        return Response({"error": "Password required"})

    pass_sha = hashlib.sha256(("unique" + password).encode()).hexdigest()

    try:
        admin = AdminUser.objects.get(password_sha256=pass_sha)
    except:
        return Response({"error": "Invalid admin password"})

    data = AdminSerializer(admin).data
    data["read_only"] = True

    return Response(data)


# ---------------------------
# CRUD: Owners
# ---------------------------
@api_view(["POST"])
def add_owner(request):
    admin_id = request.data.get("admin_id")
    name = request.data.get("name")
    sqft = request.data.get("sqft")

    admin = AdminUser.objects.get(id=admin_id)
    owner = HouseOwner(admin=admin, name=name, sqft=sqft)
    owner.save()

    return Response({"success": True})


@api_view(["POST"])
def get_owners(request):
    admin_id = request.data.get("admin_id")
    admin = AdminUser.objects.get(id=admin_id)

    return Response(OwnerSerializer(admin.owners, many=True).data)


# ---------------------------
# CRUD: Expenses
# ---------------------------
@api_view(["POST"])
def add_expense(request):
    admin_id = request.data.get("admin_id")

    admin = AdminUser.objects.get(id=admin_id)

    item = request.data.get("item")
    amount = request.data.get("amount")
    date = request.data.get("date")
    is_card = request.data.get("is_card")
    category = request.data.get("category")

    exp = Expense(
        admin=admin,
        item=item,
        amount=amount,
        date=date,
        is_card=is_card,
        category=category,
    )
    exp.save()

    return Response({"success": True})


@api_view(["POST"])
def get_expenses(request):
    admin_id = request.data.get("admin_id")
    admin = AdminUser.objects.get(id=admin_id)

    return Response(ExpenseSerializer(admin.expenses, many=True).data)


# ================= NEW VIEWS FOR BUDGET APP =================


# ---------------------------
# Budget Drafts
# ---------------------------
@api_view(["POST"])
def add_budget_draft(request):
    admin_id = request.data.get("admin_id")
    month_year = request.data.get("month_year")
    
    if not admin_id or not month_year:
        return Response({"error": "admin_id and month_year required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin not found"})
    
    draft, created = BudgetDraft.objects.get_or_create(
        admin=admin,
        month_year=month_year,
        defaults={'total_budget': 0.0}
    )
    
    if not created:
        return Response({"success": True, "draft_id": draft.id, "message": "Draft already exists"})
    
    return Response({"success": True, "draft_id": draft.id})

@api_view(["POST"])
def get_budget_drafts(request):
    admin_id = request.data.get("admin_id")
    
    if not admin_id:
        return Response({"error": "admin_id required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
        drafts = BudgetDraft.objects.filter(admin=admin)
        return Response(BudgetDraftSerializer(drafts, many=True).data)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin not found"})

@api_view(["POST"])
def get_or_create_budget_draft(request):
    admin_id = request.data.get("admin_id")
    month_year = request.data.get("month_year")
    total_budget = request.data.get("total_budget", 0.0)
    
    if not admin_id or not month_year:
        return Response({"error": "admin_id and month_year required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin not found"})
    
    draft, created = BudgetDraft.objects.get_or_create(
        admin=admin,
        month_year=month_year,
        defaults={'total_budget': total_budget}
    )
    
    # If draft exists, update total_budget if provided
    if not created and total_budget:
        draft.total_budget = total_budget
        draft.save()
    
    return Response(BudgetDraftSerializer(draft).data)

# ---------------------------
# Budget Expenses
# ---------------------------
@api_view(["POST"])
def add_budget_expense(request):
    draft_id = request.data.get("draft_id")
    
    if not draft_id:
        return Response({"error": "draft_id required"})
    
    try:
        draft = BudgetDraft.objects.get(id=draft_id)
    except BudgetDraft.DoesNotExist:
        return Response({"error": "Draft not found"})
    
    expense = BudgetExpense(
        draft=draft,
        item=request.data.get("item", ""),
        amount=request.data.get("amount", 0.0),
        date=request.data.get("date", ""),
        is_card=request.data.get("is_card", False),
        category=request.data.get("category", "General")
    )
    expense.save()
    
    return Response({"success": True, "expense_id": expense.id})

@api_view(["POST"])
def get_budget_expenses(request):
    draft_id = request.data.get("draft_id")
    
    if not draft_id:
        return Response({"error": "draft_id required"})
    
    try:
        draft = BudgetDraft.objects.get(id=draft_id)
        expenses = BudgetExpense.objects.filter(draft=draft)
        return Response(BudgetExpenseSerializer(expenses, many=True).data)
    except BudgetDraft.DoesNotExist:
        return Response({"error": "Draft not found"})

@api_view(["POST"])
def update_budget_expense(request):
    expense_id = request.data.get("expense_id")
    
    if not expense_id:
        return Response({"error": "expense_id required"})
    
    try:
        expense = BudgetExpense.objects.get(id=expense_id)
    except BudgetExpense.DoesNotExist:
        return Response({"error": "Expense not found"})
    
    # Update fields if provided
    fields_to_update = ['item', 'amount', 'date', 'is_card', 'category']
    for field in fields_to_update:
        if field in request.data:
            setattr(expense, field, request.data[field])
    
    expense.save()
    return Response({"success": True})

@api_view(["POST"])
def delete_budget_expense(request):
    expense_id = request.data.get("expense_id")
    
    if not expense_id:
        return Response({"error": "expense_id required"})
    
    try:
        expense = BudgetExpense.objects.get(id=expense_id)
        expense.delete()
        return Response({"success": True})
    except BudgetExpense.DoesNotExist:
        return Response({"error": "Expense not found"})

@api_view(["POST"])
def delete_all_budget_expenses(request):
    draft_id = request.data.get("draft_id")
    
    if not draft_id:
        return Response({"error": "draft_id required"})
    
    try:
        draft = BudgetDraft.objects.get(id=draft_id)
        BudgetExpense.objects.filter(draft=draft).delete()
        return Response({"success": True})
    except BudgetDraft.DoesNotExist:
        return Response({"error": "Draft not found"})

# ---------------------------
# Categories
# ---------------------------
@api_view(["POST"])
def get_categories(request):
    admin_id = request.data.get("admin_id")
    
    if not admin_id:
        return Response({"error": "admin_id required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
        categories = Category.objects.filter(admin=admin)
        return Response(CategorySerializer(categories, many=True).data)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin not found"})

@api_view(["POST"])
def add_category(request):
    admin_id = request.data.get("admin_id")
    name = request.data.get("name")
    
    if not admin_id or not name:
        return Response({"error": "admin_id and name required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin not found"})
    
    # Check if category already exists for this admin
    if Category.objects.filter(admin=admin, name=name).exists():
        return Response({"error": "Category already exists"})
    
    category = Category(admin=admin, name=name)
    category.save()
    
    return Response({"success": True})

@api_view(["POST"])
def delete_category(request):
    admin_id = request.data.get("admin_id")
    name = request.data.get("name")
    
    if not admin_id or not name:
        return Response({"error": "admin_id and name required"})
    
    try:
        admin = AdminUser.objects.get(id=admin_id)
        category = Category.objects.get(admin=admin, name=name)
        category.delete()
        return Response({"success": True})
    except (AdminUser.DoesNotExist, Category.DoesNotExist):
        return Response({"error": "Category not found"})
    
@api_view(["POST"])
def delete_budget_draft(request):
    draft_id = request.data.get("draft_id")
    
    if not draft_id:
        return Response({"error": "draft_id required"})
    
    try:
        draft = BudgetDraft.objects.get(id=draft_id)
        draft.delete()
        return Response({"success": True})
    except BudgetDraft.DoesNotExist:
        return Response({"error": "Draft not found"})