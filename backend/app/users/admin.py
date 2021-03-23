from django.contrib import admin

# Register your models here.
from users.models import User


@admin.register(User)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'password',)
