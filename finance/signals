from django.db.models.signals import post_migrate
from django.dispatch import receiver
from finance.models import Admin  # 你的自定义 Admin 模型

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if not Admin.objects.filter(username='admin').exists():
        print("Creating default custom admin user...")
        Admin.objects.create(username='admin', email='admin@example.com', password='adminpassword')
        print("Custom admin user created!")
    else:
        print("Custom admin user already exists.")
