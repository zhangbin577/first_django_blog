
from django.urls import path
from . import views

app_name = "notice"

urlpatterns = [
    # 通知列表
    path("list/",views.CommentNoticeListView.as_view(),name="list"),
    # 更新通知状态
    path("update/",views.CommentNoticeUpdateView.as_view(),name="update"),
]

# 注意：path()的参数2，只能接收1个函数，不要直接写"类名"，因此要调类试图的"as_views()"方法！

