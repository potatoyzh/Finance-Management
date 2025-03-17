from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Transaction, Category, Currency, Budget, Admin

# 注册模型到 Django Admin
admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(Budget)
admin.site.register(Admin)