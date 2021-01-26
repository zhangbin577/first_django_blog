
from django.urls import path
from . import views

# 正在部署的应用的名字"app_name="，Django2中必须写上！
app_name = "userprofile"

urlpatterns = [
    # 用户"登录"
    path("login/",views.user_login,name="login"),
    # 用户"登出"
    path("logout/",views.user_logout,name="logout"),
    # 用户"注册"
    path("register/",views.user_register,name="register"),
    # 用户"删除"
    path("delete/<int:id>/",views.user_delete,name="delete"),
    # 用户信息：
    path("edit/<int:id>/",views.profile_edit,name="edit"),
]
