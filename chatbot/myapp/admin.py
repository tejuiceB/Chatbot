from django.contrib import admin
from .models import UserProfile, Doctor, Blog, ChatMessage, Appointment

admin.site.register(UserProfile)
admin.site.register(Doctor)
admin.site.register(Blog)
admin.site.register(ChatMessage)
admin.site.register(Appointment)
