from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from finance.form import *
from django.db.models import Sum
from .models import *
from .decorators import *
from django.http import  JsonResponse
from django.contrib import messages
import json


# ------------------------------------------- login & register ------------------------------------------#
# -------------------------------------------------------------------------------------------------------#

# 注册
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.account_type = "regular"
            user.save()
            login(request, user)  # 自动登录
            return redirect('dashboard')  # 注册成功后跳转到主页
        else:
            print("Form errors:", form.errors)  # 调试信息，检查 Django 表单验证错误

    else:
        form = CustomUserCreationForm()

    return render(request, 'finance/register.html', {'form': form})


# 登录
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"🔹 Attempting login - Username: {username}, Password: {password}")  # 打印收到的用户名和密码

        user = authenticate(request, username=username, password=password)

        if user:
            print(f"Login successful for user: {user}")  # 打印登录成功信息
            login(request, user)
            return redirect('dashboard')  # 跳转到主页
        else:
            print("Login failed! Invalid username or password.")  # 打印失败信息
            return render(request, 'finance/login.html', {'error': 'Invalid username or password'})

    return render(request, 'finance/login.html')


# 用户登出
def logout_view(request):
    logout(request)
    return redirect('login')  # 退出后重定向到登录页面


# ------------------------------------------ dashboard --------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#


@login_required
def dashboard_view(request):
    user = request.user  # 获取当前登录用户

    # 计算交易统计数据
    total_income = Transaction.objects.filter(user=user, transaction_type="income").aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(user=user, transaction_type="expense").aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense  # 计算账户余额

    # 获取最近 5 笔交易
    recent_transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')[:5]

    return render(request, 'finance/dashboard.html', {
        'user': user,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'recent_transactions': recent_transactions,
    })



# --------------------------------------------- transaction -------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------#

# get transaction
@login_required
@login_required
def transaction_list_view(request):
    user = request.user
    sort_field = request.GET.get('sort', '-transaction_date')  # 默认按交易日期降序
    sort_direction = '' if sort_field.startswith('-') else '-'

    allowed_sort_fields = ['transaction_date', '-transaction_date', 'amount', '-amount']
    if sort_field not in allowed_sort_fields:
        sort_field = '-transaction_date'

    transactions = Transaction.objects.filter(user=user).order_by(sort_field)
    categories = Category.objects.all()  # 获取所有类别
    currencies = Currency.objects.all()

    return render(request, 'finance/transaction.html', {
        'transactions': transactions,
        'categories': categories,  # 传递类别
        'currencies': currencies,
        'current_sort': sort_field,
        'sort_direction': sort_direction,
    })


# add transaction
from django.utils.timezone import now  # 导入 Django 的时区模块


@login_required
def transaction_create_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.transaction_date = now()
            transaction.save()
            return redirect('transaction_list')
        else:
            print("Form errors:", form.errors)
    return redirect('transaction_list')


# edit transaction
@login_required
def transaction_edit_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)  # 确保当前用户只能编辑自己的交易
    categories = Category.objects.all()
    currencies = Currency.objects.all()

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)  # 绑定现有交易数据
        if form.is_valid():
            form.save()
            return redirect('transaction_list')  # 编辑成功后跳转回交易列表
    else:
        form = TransactionForm(instance=transaction)  # 让表单显示原来的交易数据

    return render(request, 'finance/edit_transaction.html', {
        'form': form,
        'transaction': transaction,  # 确保模板能拿到 `transaction.id`
        'categories': categories,
        'currencies': currencies
    })



# delete transaction
@login_required
def transaction_delete_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)  # 只能删除自己的交易

    if request.method == 'POST':  # 确保用户是通过表单提交删除
        transaction.delete()
        return redirect('transaction_list')  # 删除后回到交易列表

    return render(request, 'finance/transaction_confirm_delete.html', {'transaction': transaction})


# ------------------------------------------------- category ----------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#

@login_required
def category_list_view(request):
    categories = Category.objects.all()  # 获取所有类别
    return render(request, 'finance/categories.html', {'categories': categories})


# -------------------------------------------- user currency --------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

# display currency
def currency_list_view(request):
    currencies = Currency.objects.all()  # 获取所有货币
    return render(request, 'finance/currency_list.html', {'currencies': currencies})



#---------------------------------------------- budget management -------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

# display budget
@login_required
def budget_list_view(request):
    budgets = Budget.objects.filter(user=request.user)

    for budget in budgets:
        budget.check_budget_status()  # 每次访问时，检查并更新超支状态

    return render(request, 'finance/budget_management.html', {'budgets': budgets})


# add budget
@login_required
def budget_create_view(request):
    categories = Category.objects.all()  # 获取所有类别
    currencies = Currency.objects.all()
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user  # 关联当前用户
            budget.save()
            return redirect('budget_list')
    else:
        form = BudgetForm()

    return render(request, 'finance/budget_form.html', {'form': form, 'categories': categories , 'currencies': currencies})



# edit budget
@login_required
def budget_edit_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)  # 确保用户只能编辑自己的预算
    categories = Category.objects.all()
    currencies = Currency.objects.all()

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'finance/edit_budget.html', {'form': form, 'budget': budget, 'categories': categories, 'currencies': currencies})
2


# delete budget
@login_required
def budget_delete_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)  # 只能删除自己的预算

    if request.method == 'POST':  # 只有确认删除时才会执行
        budget.delete()
        return redirect('budget_list')

    return render(request, 'finance/budget_confirm_delete.html', {'budget': budget})


# --------------------------------------------------------- admin  ---------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------#

from django.shortcuts import render, redirect
from finance.models import Admin  # 确保导入 Admin 模型
import logging

# 设置日志
logger = logging.getLogger(__name__)

def admin_login_view(request):
    """
    管理员登录视图
    """
    # **🔹 获取数据库中的所有管理员并打印**
    admins = Admin.objects.all()
    print("当前数据库中的管理员用户：")
    for admin in admins:
        print(f"🔹 ID: {admin.id}, Username: {admin.username}, Email: {admin.email}, Password: {admin.password}")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"🔹 Received POST request - Username: {username}, Password: {password}")  # 打印请求数据

        admin = Admin.objects.filter(username=username).first()

        if admin:
            print(f"账号存在 - ID: {admin.id}, Username: {admin.username}, Email: {admin.email}")
        else:
            print("未找到该管理员账户")

        if admin and admin.password == password:  # 这里应该使用哈希加密验证
            request.session['is_admin'] = True  # 存储管理员身份
            request.session['admin_id'] = admin.id  # 存储 Admin ID

            print("Admin 登录成功，重定向到 admin_user_list")  # 调试信息
            return redirect('admin_user_list')  # 确保 URL 名称正确
        else:
            print("登录失败: 用户名或密码错误")  # 调试信息
            return render(request, 'finance/admin_login.html', {'error': '管理员用户名或密码错误'})

    print("GET 请求 - 显示 Admin 登录页面")  # 调试信息
    return render(request, 'finance/admin_login.html')



# admin user list

@admin_required
def admin_user_list_view(request):
    users = User.objects.all()  # 获取所有普通用户
    return render(request, 'finance/user_management.html', {'users': users})

# admin user delete

@admin_required
def admin_user_delete_view(request, user_id):
    user = get_object_or_404(User, id=user_id)  # 只允许删除普通用户
    if request.method == 'POST':
        user.delete()
        return redirect('admin_user_list')

    return render(request, 'finance/admin_user_confirm_delete.html', {'user': user})

# admin transaction list

@admin_required
def admin_transaction_list_view(request):
    transactions = Transaction.objects.all()  # 获取所有交易
    return render(request, 'finance/admin_transaction.html', {'transactions': transactions})

# admin transaction delete

@admin_required
def admin_transaction_delete_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':  # 需要确认删除
        transaction.delete()
        return redirect('admin_transaction_list')

    return render(request, 'finance/admin_transaction.html', {'transaction': transaction})

# admin category list

@admin_required
def admin_category_list_view(request):
    categories = Category.objects.all()  # 获取所有类别
    return render(request, 'finance/categories.html', {'categories': categories})

# admin add category

@admin_required
def admin_category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form = CategoryForm()

    return render(request, 'finance/admin_category.html', {'form': form})

# admin edit category
@admin_required
def admin_category_edit_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'finance/categories.html', {'form': form})

# admin delete category

@admin_required
def admin_category_delete_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':  # 需要确认删除
        category.delete()
        return redirect('admin_category_list')

    return render(request, 'finance/admin_category_confirm_delete.html', {'category': category})


# admin currency list
@admin_required
def admin_currency_list_view(request):
    currencies = Currency.objects.all()  # 获取所有货币
    return render(request, 'finance/currency_management.html', {'currencies': currencies})

# admin add currency
@admin_required
def admin_currency_create_view(request):
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_currency_list')
    else:
        form = CurrencyForm()

    return render(request, 'finance/admin_currency_form.html', {'form': form})

# admin edit currency
@admin_required
def admin_currency_edit_view(request, currency_id):
    currency = get_object_or_404(Currency, id=currency_id)

    if request.method == 'POST':
        new_rate = request.POST.get('currency_rate')

        if new_rate and float(new_rate) > 0:
            currency.currency_rate = float(new_rate)
            currency.save()
            messages.success(request, f"{currency.currency_name} exchange rate updated successfully.")
        else:
            messages.error(request, "Invalid exchange rate.")

    return redirect('admin_currency_list')  # 成功后跳转回货币列表


# admin delete currency
@admin_required
def admin_currency_delete_view(request, currency_id):
    currency = get_object_or_404(Currency, id=currency_id)

    if request.method == 'POST':  # 需要确认删除
        currency.delete()
        return redirect('admin_currency_list')

    return render(request, 'finance/admin_currency_confirm_delete.html', {'currency': currency})


# admin budget list
@admin_required
def admin_budget_list_view(request):
    budgets = Budget.objects.all()  # 获取所有用户的预算
    return render(request, 'finance/admin_budget.html', {'budgets': budgets})

# admin delete budget
@admin_required
def admin_budget_delete_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id)

    if request.method == 'POST':  # 需要确认删除
        budget.delete()
        return redirect('admin_budget_list')

    return render(request, 'finance/admin_budget_confirm_delete.html', {'budget': budget})


# -------------------------------------------------------- statistic ----------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------#


@login_required
def statistics_view(request):
    user = request.user  # 只获取当前用户的数据

    # 收入/支出的饼状图数据
    income_data = Transaction.objects.filter(user=user, transaction_type='income') \
        .values('category__category_name') \
        .annotate(total_amount=Sum('amount'))

    expense_data = Transaction.objects.filter(user=user, transaction_type='expense') \
        .values('category__category_name') \
        .annotate(total_amount=Sum('amount'))

    income_labels = [entry['category__category_name'] for entry in income_data]
    income_values = [float(entry['total_amount']) for entry in income_data]

    expense_labels = [entry['category__category_name'] for entry in expense_data]
    expense_values = [float(entry['total_amount']) for entry in expense_data]

    # 每月收入/支出的折线图数据
    monthly_income = Transaction.objects.filter(user=user, transaction_type='income') \
        .extra({'month': "strftime('%%Y-%%m', transaction_date)"}) \
        .values('month') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('month')

    monthly_expense = Transaction.objects.filter(user=user, transaction_type='expense') \
        .extra({'month': "strftime('%%Y-%%m', transaction_date)"}) \
        .values('month') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('month')

    months = sorted(set(entry['month'] for entry in monthly_income) | set(entry['month'] for entry in monthly_expense))

    income_by_month = {entry['month']: float(entry['total_amount']) for entry in monthly_income}
    expense_by_month = {entry['month']: float(entry['total_amount']) for entry in monthly_expense}

    income_chart_values = [income_by_month.get(month, 0) for month in months]
    expense_chart_values = [expense_by_month.get(month, 0) for month in months]

    return render(request, 'finance/statistics.html', {
        'income_labels': json.dumps(income_labels),
        'income_values': json.dumps(income_values),
        'expense_labels': json.dumps(expense_labels),
        'expense_values': json.dumps(expense_values),
        'months': json.dumps(months),
        'income_chart_values': json.dumps(income_chart_values),
        'expense_chart_values': json.dumps(expense_chart_values),
    })
