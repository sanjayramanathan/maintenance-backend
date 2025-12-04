from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AdminUser, HouseOwner, Expense
from .serializers import AdminSerializer, OwnerSerializer, ExpenseSerializer
import hashlib

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
