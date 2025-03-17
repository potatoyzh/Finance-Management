from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):  # 确保用户是管理员
            return redirect('admin_login')  # 不是管理员，跳转到登录
        return view_func(request, *args, **kwargs)
    return wrapper
