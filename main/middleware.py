from django.http import HttpResponse
from django.db import connection

class DatabaseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the database is available
        try:
            with connection.cursor() as cursor:
                # Update this to use the correct table name
                cursor.execute("SELECT 1 FROM main_userprofile LIMIT 1")
        except Exception as e:
            # Handle the error appropriately
            print(f"Database error: {e}")
            # You might want to return an error response here
            
        response = self.get_response(request)
        return response