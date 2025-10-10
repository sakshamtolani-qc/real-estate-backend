from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    
    def ready(self):
        # Import signals to register them
        import leads.notification_helpers
