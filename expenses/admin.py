from django.contrib import admin
from expenses.models import Transfert, Bill, ExtendedUser, Category, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class ExtendedUserInline(admin.StackedInline):
    model = ExtendedUser

class UserAdmin(UserAdmin):
    inlines = (ExtendedUserInline, )
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register([Transfert, Bill, Category])
