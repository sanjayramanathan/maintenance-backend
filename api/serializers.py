from rest_framework import serializers
from .models import AdminUser, HouseOwner, Expense

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseOwner
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"

class AdminSerializer(serializers.ModelSerializer):
    owners = OwnerSerializer(many=True, read_only=True)
    expenses = ExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = AdminUser
        fields = "__all__"
