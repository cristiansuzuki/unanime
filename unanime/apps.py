from django.apps import AppConfig

class UnanimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unanime'   # 🔥 TEM que ser exatamente o nome da pasta

    def ready(self):
        import unanime.signals
