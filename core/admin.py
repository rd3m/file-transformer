from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ProcessedFile


class ProcessedFileInline(admin.TabularInline):
    model = ProcessedFile
    extra = 0
    exclude = ("file_name",)
    readonly_fields = ("prompt", "generated_code")
    ordering = ("-date_added",)


class CustomUserAdmin(UserAdmin):
    inlines = (ProcessedFileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
