from django.http import JsonResponse
import django.db.utils  
from django.core.exceptions import ObjectDoesNotExist

def create_admin_user(request):
    try:
        from finance.models import Admin

        if not Admin.objects.filter(username='admin123').exists():
            Admin.objects.create(
                username='admin123',
                email='admin123@example.com',
                password='AdminPassword123'
            )
            return JsonResponse({'message': 'Custom Admin user created successfully!'})
        else:
            return JsonResponse({'message': 'Custom Admin user already exists.'})
    
    except (django.db.utils.OperationalError, django.db.utils.ProgrammingError, ObjectDoesNotExist):
        return JsonResponse({'error': 'Database not ready. Try again after migrations.'}, status=500)

