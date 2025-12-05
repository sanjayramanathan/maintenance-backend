from django.db import models
import hashlib

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=200)
    password_sha256 = models.CharField(max_length=64, unique=True)

    # rate mode
    is_flat_rate = models.BooleanField(default=True)
    flat_amount = models.FloatField(default=0)
    per_sqft_rate = models.FloatField(default=0)

    def set_password(self, raw):
        # password for login
        self.password_hash = hashlib.sha256(raw.encode()).hexdigest()

        # enforce uniqueness
        self.password_sha256 = hashlib.sha256(("unique" + raw).encode()).hexdigest()

    def check_password(self, raw):
        return self.password_hash == hashlib.sha256(raw.encode()).hexdigest()

    def __str__(self):
        return self.username


class HouseOwner(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name="owners")
    name = models.CharField(max_length=150)
    sqft = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Expense(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name="expenses")
    item = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.CharField(max_length=20)
    is_card = models.BooleanField(default=False)
    category = models.CharField(max_length=100, default="General")

    def __str__(self):
        return self.item


# ================= NEW MODELS FOR BUDGET APP =================

class BudgetDraft(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name="budget_drafts")
    month_year = models.CharField(max_length=100)  # e.g., "January 2024"
    total_budget = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('admin', 'month_year')  # One draft per admin per month
    
    def __str__(self):
        return f"{self.month_year} (₹{self.total_budget})"


class BudgetExpense(models.Model):
    draft = models.ForeignKey(BudgetDraft, on_delete=models.CASCADE, related_name="expenses")
    item = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.CharField(max_length=20)
    is_card = models.BooleanField(default=False)
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.item} - ₹{self.amount}"


class Category(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('admin', 'name')  # Unique category per admin
    
    def __str__(self):
        return self.name