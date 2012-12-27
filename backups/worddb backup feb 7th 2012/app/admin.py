
from app.models import User
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'email', 'password')


admin.site.register(User, UserAdmin)