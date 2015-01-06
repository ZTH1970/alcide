from django.apps import AppConfig


class DossiersConfig(AppConfig):
    name = 'calebasse.dossiers'

    def ready(self):
        PatientRecord = self.get_model('PatientRecord')
        PatientRecord.DEFICIENCY_FIELDS = [field for field in PatientRecord._meta.get_all_field_names() if field.startswith('deficiency_')]
        PatientRecord.MISES_FIELDS = [field for field in PatientRecord._meta.get_all_field_names() if field.startswith('mises_')]


default_app_config = 'calebasse.dossiers.DossiersConfig'
