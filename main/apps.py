frofrom django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'  # <-- THIS LINE IS CRITICAL

    def ready(self):
        import main.signals