from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        from finance.models import Admin  # 你的自定义 Admin 模型

        try:
            if not Admin.objects.filter(username='admin').exists():
                Admin.objects.create(
                    username='admin',
                    email='admin@example.com',
                    password='AdminPassword123'  # 这里要加密
                )
                print("Default custom admin user created successfully.")
        except (OperationalError, ProgrammingError):
            pass
