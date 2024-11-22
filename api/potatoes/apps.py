from django.apps import AppConfig


class PotatoesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "potatoes"

    def ready(self):
        import potatoes.signals
