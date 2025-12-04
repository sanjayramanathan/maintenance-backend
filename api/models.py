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
