from rest_framework import serializers
from .models import AdminUser, HouseOwner, Expense, BudgetDraft, BudgetExpense, Category

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseOwner
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"

# ================= NEW SERIALIZERS FOR BUDGET APP =================

class BudgetDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetDraft
        fields = "__all__"

class BudgetExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetExpense
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

# ==================================================================

class AdminSerializer(serializers.ModelSerializer):
    owners = OwnerSerializer(many=True, read_only=True)
    expenses = ExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = AdminUser
        fields = "__all__"