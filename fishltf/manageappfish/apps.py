from django.apps import AppConfig



class ManageappfishConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manageappfish'

    def ready(self):
        # Импортируем сигналы только после полной загрузки приложения
        import manageappfish.signals  # Замените `your_app` на имя вашего приложени



