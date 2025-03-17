from django.http import JsonResponse
from finance.models import Admin

def create_admin_user(request):
    if not Admin.objects.filter(username='admin').exists():
        Admin.objects.create(
            username='admin123',
            email='admin123@example.com',
            password='AdminPassword123'
        )
        return JsonResponse({'message': 'Custom Admin user created successfully!'})
    else:
        return JsonResponse({'message': 'Custom Admin user already exists.'})

