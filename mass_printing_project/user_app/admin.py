from django.contrib import admin
from user_app.models import File,ExtractedData,ExtractedAdvisor

admin.site.register(File)
admin.site.register(ExtractedData)
admin.site.register(ExtractedAdvisor)
