from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *


# --------------------------------- user form -----------------------------------------------------------------#


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # 确保注册时用户必须输入 email

    class Meta:
        model = User  # 继承你的自定义 User 模型
        fields = ['username', 'email', 'password1', 'password2']  # 让表单包含 email 字段


# ------------------------------------ transaction form ---------------------------------------------------#

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'currency', 'amount', 'transaction_type', 'description']


# ------------------------------------------- currency ------------------------------------------------------#

class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['currency_name', 'currency_rate']


# ------------------------------------------ budget -------------------------------------------------------------#

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount_limit', 'start_date', 'end_date', 'currency']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

# ----------------------------------------- category ----------------------------------------------------------#

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_type']  # 让管理员选择类别名称 & 类型