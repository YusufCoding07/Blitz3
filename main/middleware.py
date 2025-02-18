from django.http import HttpResponse
from django.db import connection

class DatabaseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM main_profile LIMIT 1")
            return self.get_response(request)
        except Exception as e:
            return HttpResponse(f"Database error: {str(e)}", status=500)