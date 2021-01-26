from django.contrib import admin


# Register your models here.
from .models import Profile

# 解决直接"admin.site.register(Profile)："导致的User、Profile是两个分开的表的问题！
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


# 定义1个行内"admin"
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "UserProfile"


# 将"Profile"关联到"User"中
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# 重新注册：User
admin.site.unregister(User)
admin.site.register(User,UserAdmin)  # 这样：就将"User、Profile"两张表，合并为一张完整的表！

# 不信：后台admin的User表中，发现Profile的数据就"堆叠"在底部了！
