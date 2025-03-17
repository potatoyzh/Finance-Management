from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser, Group, Permission

# 用户模型
class User(AbstractUser):
    account_type = models.CharField(
        max_length=10,
            choices=[("regular", "Regular"), ("premium", "Premium")]
    )
    # 移除 groups 和 user_permissions，防止冲突
    groups = None
    user_permissions = None

# 交易（收入/支出）
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[("income", "Income"), ("expense", "Expense")])
    transaction_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)

# 交易类别
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=[("income", "Income"), ("expense", "Expense")])

    def __str__(self):
        return self.category_name

# 货币及汇率
class Currency(models.Model):
    currency_name = models.CharField(max_length=50, unique=True)
    currency_rate = models.DecimalField(max_digits=10, decimal_places=4)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.currency_name

# 预算管理
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 预算属于哪个用户
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # 预算属于哪个类别
    amount_limit = models.DecimalField(max_digits=10, decimal_places=2)  # 预算金额
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True) # 预算货币
    start_date = models.DateField()  # 预算开始时间
    end_date = models.DateField()  # 预算结束时间
    is_exceeded = models.BooleanField(default=False)  # 是否超支

    def check_budget_status(self):
        total_expense = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type="expense",
            transaction_date__range=[self.start_date, self.end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        self.is_exceeded = total_expense > self.amount_limit
        self.save()  # 保存最新的 `is_exceeded` 状态


# 管理员
class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # 存储密码

    def __str__(self):
        return self.username
