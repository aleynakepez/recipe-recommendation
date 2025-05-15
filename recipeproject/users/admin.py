from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

#hazır admin arayüzü kullanmak için 
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "is_active", "is_staff") #admin paneli sütunları
    list_filter = ("is_active", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (            #Kullanıcı Güncelleme Görünümü
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff"),
        }),
    )

class ProfileAdmin(admin.ModelAdmin):
      model = Profile
      list_display = ("user", "nickname", "avatar")
      search_fields = ("user__email", "nickname")
      list_filter = ("nickname",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin) # modellerin admin paneline eklenmesini sağlar
