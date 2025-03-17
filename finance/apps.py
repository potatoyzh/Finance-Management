from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import ObjectDoesNotExist

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        from finance.models import Admin  # 你的自定义 Admin 模型

        try:
            admin_email = 'admin@example.com'
            if not Admin.objects.filter(email=admin_email).exists():
                Admin.objects.create(
                    username='admin',
                    email=admin_email,
                    password='AdminPassword123'
                )
                print("✅ Default custom admin user created successfully.")
            else:
                print("⚠️ Custom admin user already exists. Skipping creation.")
        except (OperationalError, ProgrammingError):
            # 数据库还没迁移时避免报错
            pass
