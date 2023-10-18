from django.contrib import admin
from .models import Document, DocumentErrorDetail, DocumentErrorStat, UserProfile,VerificationCode
# Register your models here.

admin.site.register(Document)
admin.site.register(DocumentErrorDetail)
admin.site.register(DocumentErrorStat)
admin.site.register(UserProfile)
admin.site.register(VerificationCode)