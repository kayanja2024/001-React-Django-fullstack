from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None,{
            'classes': ( 'wide',),
            'fields': ( 'username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'city', 'state', 'address', 'phone', 'is_staff', 'is_active') 
        })
    )

admin.site.register(CustomUser, CustomUserAdmin)




# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'email', 'first_name', 'last_name', 'city', 'state', 'address')  # Include your custom fields here
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('city', 'state', 'address')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('city', 'state', 'address')}),
#     )

# admin.site.register(CustomUser, CustomUserAdmin)



# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'email', 'first_name', 'last_name', 'city', 'state', 'address')  # Include the new fields here
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('city', 'state', 'address')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('city', 'state', 'address')}),
#     )

# admin.site.register(CustomUser, CustomUserAdmin)
