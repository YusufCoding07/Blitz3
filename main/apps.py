from django.apps import AppConfig

class MainConfig(AppConfig):
    # ... other config ...
    def ready(self):
        import main.signals  # Ensure this line exists
        print("🔌 Signals registered!")  # Debug log