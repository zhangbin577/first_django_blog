
from django.urls import path

from . import views

# 正在部署的应用的名字"app_name="，Django2中必须写上！
app_name = "article"

urlpatterns = [
    # 文章列表页
    path("article-list/",views.article_list,name="article_list"),
    # 文章详情 (Django2：path的新语法，类似"flask"的带参数的路由)
    path("article-detail/<int:id>/",views.article_detail,name="article_detail"),
    # Forms：写文章
    path("article-create/",views.article_create,name="article_create"),
    # 删除文章
    # path("article-delete/<int:id>/",views.article_delete,name="article_delete"),
    # post防csrf攻击：安全删除文章
    path("article-safe-delete/<int:id>/",views.article_safe_delete,name="article_safe_delete"),
    # 修改：更新文章
    path("article-update/<int:id>/",views.article_update,name="article_update"),

    # 点赞+1
    path("increase-likes/<int:id>/",views.IncreaseLikesView.as_view(),name="increase_likes"),
]

