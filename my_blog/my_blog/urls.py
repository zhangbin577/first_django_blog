"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
import notifications.urls


urlpatterns = [
    path('admin/', admin.site.urls),

    # "article"模块的：url访问路径
    path("article/",include("article.urls",namespace="article")),
    # "userprofile"用户管理模块的：url访问路径
    path("userprofile/",include("userprofile.urls",namespace="userprofile")),
    # 第3方app："Django-password-reset"(重置密码)
    path("password-reset/",include("password_reset.urls")),
    # "comment"：评论模块的url
    path("comment/",include("comment.urls",namespace="comment")),

    # 评论的：消息通知 ——————————————————注意：不再是字符串，为确保模块，安装到正确的namespace中！
    path("inbox/notifications/",include(notifications.urls,namespace="notifications")),

    # 消息通知app：集中处理"已读/未读"
    path("notice/",include("notice.urls",namespace="notice")),

    # 添加第3方app："django-allauth库"，实现blog第三方登录！
    path("accounts/",include("allauth.urls")),
]

# 处理MEDIAL_URL中的：媒体文件，如Profile()中，用户头像"avatar"
from django.conf import settings
from django.conf.urls.static import static
# 这样：就为以后上传的图片，配置好了url路径
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


# 设置blog网站"首页"
from article.views import article_list
urlpatterns += [
    path("",article_list,name="home"),
]


