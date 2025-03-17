from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),  # 用户注册
    path('login/', login_view, name='login'),  # 使用自己写的 login_view
    path('logout/', logout_view, name='logout'),  # 使用自己写的 logout_view
    path('dashboard/', dashboard_view, name='dashboard'),  # 用户主页
    path('transactions/', transaction_list_view, name='transaction_list'),
    path('transactions/add/', transaction_create_view, name='transaction_create'),
    path('transactions/edit/<int:transaction_id>/', transaction_edit_view, name='transaction_edit'),
    path('transactions/delete/<int:transaction_id>/', transaction_delete_view, name='transaction_delete'),
    path('currencies/', currency_list_view, name='currency_list'),  # 查看货币列表
    path('budgets/', budget_list_view, name='budget_list'),
    path('budgets/new/', budget_create_view, name='budget_create'),
    path('budgets/edit/<int:budget_id>/', budget_edit_view, name='budget_edit'),
    path('budgets/delete/<int:budget_id>/', budget_delete_view, name='budget_delete'),
    path('admin_custome/users/', admin_user_list_view, name='admin_user_list'),  # 管理员查看用户
    path('admin_custome/users/delete/<int:user_id>/', admin_user_delete_view, name='admin_user_delete'),  # 删除用户
    path('admin_custome/transactions/', admin_transaction_list_view, name='admin_transaction_list'),  # 管理员查看交易
    path('admin_custome/transactions/delete/<int:transaction_id>/', admin_transaction_delete_view, name='admin_transaction_delete'),  # 删除交易
    path('admin_custome/categories/', admin_category_list_view, name='admin_category_list'),  # 管理员查看类别
    path('admin_custome/categories/new/', admin_category_create_view, name='admin_category_create'),  # 添加类别
    path('admin_custome/categories/edit/<int:category_id>/', admin_category_edit_view, name='admin_category_edit'),  # 修改类别
    path('admin_custome/categories/delete/<int:category_id>/', admin_category_delete_view, name='admin_category_delete'),  # 删除类别
    path('admin_custome/currencies/', admin_currency_list_view, name='admin_currency_list'),  # 管理员查看货币
    path('admin_custome/currencies/new/', admin_currency_create_view, name='admin_currency_create'),  # 添加货币
    path('admin_custome/currencies/edit/<int:currency_id>/', admin_currency_edit_view, name='admin_currency_edit'),  # 修改货币
    path('admin_custome/currencies/delete/<int:currency_id>/', admin_currency_delete_view, name='admin_currency_delete'),  # 删除货币
    path('admin_custome/budgets/', admin_budget_list_view, name='admin_budget_list'),  # 管理员查看预算
    path('admin_custome/budgets/delete/<int:budget_id>/', admin_budget_delete_view, name='admin_budget_delete'),  # 删除预算
    path('categories/', category_list_view, name='categories'),# 类型查看
    path('admin_custome/login/', admin_login_view, name='admin_login'),
    path('statistics/', statistics_view, name='statistics'),
]
