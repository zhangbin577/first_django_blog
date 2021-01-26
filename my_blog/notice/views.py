from django.shortcuts import render,redirect

# Create your views here.
# 这里：我们学习使用"类视图"写法，不采用传统的"视图函数"！！！(具体看Django文档)

from article.models import ArticlePost
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


# 通知列表                # 继承"混入类Mixin"：要求调此视图必"先登录"！
class CommentNoticeListView(LoginRequiredMixin,ListView):
    # 上下文名称
    context_object_name = "notices"
    # 模板的位置
    template_name = "notice/list.html"
    # 登录重定项
    login_url = "/userprofile/login/"

    # 未读通知的"查询集"：覆写"get_queryset()"方法，返回传给模板的"未读通知对象"！
    def get_queryset(self):
        return self.request.user.notifications.unread()

# 混入类"Mixin"：指具有某些功能、通常不独立使用、提供给其他类继承功能的类。就是“混入”的意思。


# 更新：通知状态
class CommentNoticeUpdateView(View):
    # 处理get请求
    def get(self,request):
        # 获取：未读消息
        notice_id = request.GET.get("notice_id")
        # 更新：单条通知
        if notice_id:
            article = ArticlePost.objects.get(id=request.GET.get("article_id"))
            request.user.notifications.get(id=notice_id).mark_as_read()

            # 参数是model对象时,会自动调model的"get_absolute_url()方法"注意：和重定url的原理一样，只是这里"换种"实现方式！
            return redirect(article)
        # 更新：全部通知
        else:
            request.user.notifications.mark_all_as_read()
            return redirect("notice:list")

# mark_as_read()/all_as_read()：是notifications模块提供的方法，用于将未读通知转换为"已读"！


