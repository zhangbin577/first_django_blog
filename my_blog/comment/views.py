from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse  # 引入"JsonResponse",json响应格式！
from article.models import ArticlePost
from .forms import CommentForm
# 引入：Comment
from .models import Comment
# 引入：评论的"消息通知"
from notifications.signals import notify
from django.contrib.auth.models import User


# 文章"评论" ———————修改：实现"多级评论"，新增"parent_comment_id"参数(用于区分评论级，有缺省值None)
@login_required(login_url="userprofile/login/")
def post_comment(request,article_id,parent_comment_id=None):

    article = get_object_or_404(ArticlePost,id=article_id)
    # get_object_or_404()：和Model.objects.get()功能相同。
    # 区别：若用户请求个不存在的对象objects()会返回"Error500(服务器内部错误)"，而404()会返回"Error404"错误更精准！

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user

            # 新增：二级回复处理，parent_comment_id=None为"1级父"，有具体值则为"多级"！
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若：回复层级>2级，则转为2级
                # 用MPTT的get_root()：将其父级重置为树形结构最底部的1级评论，
                new_comment.parent_id = parent_comment.get_root().id
                # 保存：实际"被回复"人user
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 新增：给其它用户，发送"消息通知"——————"用户间"：被评论通知！
                if not parent_comment.user.is_superuser:
                    notify.send(request.user,recipient=parent_comment.user,
                                 verb="回复了你",target=article,action_object=new_comment)

                # 修改：解决"2级评论"，锚点定位
                # return HttpResponse("200 OK!")
                return JsonResponse({"code":"200 OK!","new_comment_id":new_comment.id})

            # 再真正保存
            new_comment.save()

            # 新增：给管理员，发送"消息通知" ———————文章"作者"：被评论通知！
            if not request.user.is_superuser:
                notify.send(request.user,recipient=User.objects.filter(is_superuser=1),
                            verb="回复了你",target=article,action_object=new_comment)

            # 新增：视图中拼接，评论"锚点"定位(1级评论)
            redirect_url = article.get_absolute_url() + "#comment_elem_" + str(new_comment.id)

            # 用户评论后，回到文章"详情页"url中：当参数是model对象时,会自动调model的"get_absolute_url()方法"！
            # 因此：要在article-models.py中添上此函数。注意：和重定url的原理一样，只是这里"换种"实现方式！
            # 修改：redirect()参数，不直接传入model了
            return redirect(redirect_url)
        else:
            return HttpResponse("表单内容有误，请重新填写！")

    # 新增：get请求处理，给2级回复，提供空白的表单！
    elif request.method == "GET":
        comment_form = CommentForm()
        context = {
            "comment_form":comment_form,
            "article_id":article_id,
            "parent_comment_id":parent_comment_id,
        }
        return render(request,"comment/reply.html",context)

    # 处理：其它请求
    else:
        return HttpResponse("发表评论，仅接受post/get请求！")

