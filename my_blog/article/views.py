
from django.shortcuts import render, redirect,get_object_or_404

# Create your views here.
# 文章视图：博客首页、内容详情页、评论的操作页

from .models import ArticlePost
# 引入markdown模块：是1种轻量级标记语言，允许人用易写的纯文本格式写文档。
# Markdown编写的文档,可导出HTML/Word/PDF等多种格式的文档(编写的文档后缀为".md/.markdown")
import markdown
from .forms import ArticlePostForm  # 引入"Forms表单类"
from django.http import HttpResponse
from django.contrib.auth.models import User
# 引入：Django的"Paginator"分页器模块
from django.core.paginator import Paginator
# 引入：Q对象 (查询条件中，完成"or"操作)
from django.db.models import Q


# 文章：列表页 ——————修改：文章"分页"处理、文章"热度"排序显示、搜索"特定类型"文章
def article_list(request):
    # 从请求url中：提取查询参数
    search = request.GET.get("search")
    order = request.GET.get("order")
    column = request.GET.get("column")
    tag = request.GET.get("tag")

    # 初始化查询集：取出所有博客文章
    article_list = ArticlePost.objects.all()

    # 查询集"搜索"
    if search:
        # 用Q查询：进行联合搜索，查询谓词"icontains"是不区分大小写的"包含"——————常用于：filter()不等值条件查询！
        article_list = article_list.filter(Q(title__icontains=search)|Q(body__icontains=search))
    else:
        # 将search参数重置为空：必须有！不然用户没操作，则search=None，传到模板会是"None"字符串，有值了！！！
        search = ""
    # 查询集"排序"
    if order == "total_views":
        article_list = article_list.order_by("-total_views")
    # 查询集"栏目"
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    # 查询集"标签"
    if tag and tag != "None":
        # filter()：Django-taggit中标签过滤的写法！意思是"tags字段中过滤name为tag的数据条目"。
        article_list = article_list.filter(tags__name__in=[tag])

    # 每页：只显示1篇"文章"
    paginator = Paginator(article_list,3)
    # 获取：url中的页码"page"
    page = request.GET.get("page","None!")
    # 将导航对象相应的页码内容，返回给articles
    articles = paginator.get_page(page)

    # 传递给模板  (新增order、新增search)
    context = {"articleAll": articles,"order":order,"search":search,"column":column,"tag":tag}
    return render(request,"article/list.html",context)


from comment.models import Comment
# 前台使用"Ckeditor"编辑器
from comment.forms import CommentForm

# 文章：详情页 (函数传入"id"参数) ——————修改：引入文章"浏览量"、引入文章"目录"、新增"评论"内容
def article_detail(request,id):

    # filer()：取出文章评论
    comments = Comment.objects.filter(article=id)

    # 取出对应的文章
    # article = ArticlePost.objects.get(id=id)
    article = get_object_or_404(ArticlePost,id=id)

    # 将markdown语法：渲染成"html"样式；markdown(text,**kwargs):参数1=要渲染的"内容"，参数2=要用的"语法扩展"

    # 修改：Markdown的语法渲染，实现可把文章"目录"，插到页面的"任意"位置
    # 实现：通过"convert()方法"，将bodd正文渲染成html页面，再通过md.toc将"目录"传递给模板！
    md = markdown.Markdown(
                        extensions=[
                         # extra包含：缩写、表格等常用扩展
                         "markdown.extensions.extra",
                         # codehilite：语法高亮扩展
                         "markdown.extensions.codehilite",
                         # 新增：toc目录扩展
                         "markdown.extensions.toc",
                        ])
    article.body = md.convert(article.body)

    # 浏览量：+1 ——————：update_fields=[]，指定了数据库只更新total_views字段
    article.total_views += 1
    article.save(update_fields=["total_views"])

    # 传递给模板 ——————：新增"md.toc"对象
    # 引入评论表单
    comment_form = CommentForm()
    context = {"article": article,"toc":md.toc,"comments":comments,"comment_form":comment_form}
    return render(request,"article/detail.html",context)


# 引入：验证登录的"装饰器" ——————：对用户的登录状态进行检查！
from django.contrib.auth.decorators import login_required
from .models import ArticleColumn


# Forms表单：写文章的视图 (创建文章)
@login_required(login_url="/userprofile/login")  # 装饰器：登录了，才会执行此"写文章"的函数
def article_create(request):
    # 用户提交数据
    if request.method == "POST":
        # 将提交的post数据，赋给表单实例 ——————增加：request.FILES属性(文章"标题图")
        article_post_form = ArticlePostForm(request.POST,request.FILES)
        # Django内置的"is_valid()",判断数据是否满足表单模型的要求(=True)
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库(commit=False)，author还未指定！
            new_article = article_post_form.save(commit=False)
            # 指定作者：为id=1的用户
            # new_article.author = User.objects.get(id=1)
            # 指定：目前登录的用户，为文章"作者" (登录状态检查)
            new_article.author = User.objects.get(id=request.user.id)

            # 新增：文章"栏目"表单处理 ——————判断：是否有"栏目"(某些文章是没有栏目的，none)
            if request.POST["column"] != "none":                # 即id是：value="{{ column.id }}"
                new_article.column = ArticleColumn.objects.get(id=request.POST["column"])

            # 将新文章：保存到数据库
            new_article.save()

            # 新增：文章"标签"，保存tags的"多对多"关系
            # 注意：提交的表单用了commit=False选项，则必须调save_m2m()才能正确的保存标签！
            article_post_form.save_m2m()

            # 完成后：url反向解析，回到文章"列表页"查看
            return redirect("article:article_list")
        # 不满足：=False
        else:
            return HttpResponse("表单内容有误，请重新填写！")
    # 用户请求获取数据
    else:
        # 建："空"表单实例
        article_post_form = ArticlePostForm()

        # 新增：文章"栏目"的上下文
        columns = ArticleColumn.objects.all()

        # 传递："写文章"的模板页
        context = {"article_form": article_post_form,"columns":columns}
        return render(request,"article/create.html",context)


# 删除文章 (传入文章的"id")
# def article_delete(request,id):
#     article = ArticlePost.objects.get(id=id)
#     article.delete()
#     return redirect("article:article_list")

# post防csrf攻击："安全"删除文章
@login_required(login_url="/userprofile/login")  # 装饰器：登录了，才会执行此"删除文章"的函数
def article_safe_delete(request,id):
    if request.method == "POST":
        # 根据id：获取需要删除的文章
        article = ArticlePost.objects.get(id=id)

        # 过滤：非作者的用户
        if request.user != article.auhtor:
            return HttpResponse("抱歉，您无权删除这篇文章！")

        # ORM：数据库中删除"单个"对象
        article.delete()
        # 完成删除后，返回到文章"列表页"
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求删除文章！")


# 修改：更新文章 (传入当前文章的id)
@login_required(login_url="/userprofile/login")  # 装饰器：登录了，才会执行此"修改文章"的函数
def article_update(request,id):
    """
    POST方法：提交表单，更新"title、body"字段
    GET方法：进入初始表单页面
    """
    # 获取：需修改的文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤："非作者"的用户
    if request.user != article.author:
        return HttpResponse("抱歉，您无权修改这篇文章！")

    if request.method == "POST":
        # 将提交的post数据，赋给表单实例
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断：是否满足模型要求
        if article_post_form.is_valid():
            # 保存：article对象的"新title、新body"
            article.title = request.POST["title"]
            article.body = request.POST["body"]

            # 新增：文章"栏目"表单处理 ——————判断：是否有"栏目"(某些文章是没有栏目的，none)
            if request.POST["column"] != "none":
                article.column = ArticleColumn.objects.get(id=request.POST["column"])
            else:
                article.column = None

            # 新增：文章"标题图"、文章"标签"处理
            if request.FILES.get("avatar"):
                article.avatar = request.FILES.get("avatar")
            # tags.set():是库提供的接口，用于更新"标签名"。注意tags.set()是如何将序列分隔并解包的。
            article.tags.set(*request.POST.get('tags').split(','),clear=True)

            article.save()
            # 返回到：修改后的文章详情中 (需传入它的id跳转)
            return redirect("article:article_detail",id=id)
        else:
            return HttpResponse("表单内容：修改有误，请重填提交！")
    else:
        # 创建表单实例
        article_post_form = ArticlePostForm()

        # 新增：文章"栏目"的上下文
        columns = ArticleColumn.objects.all()
        # tags.names()：也是库提供的接口，用于"获取"标签名。渲染"空表单"时,用了列表生成器将数据转换为字符串。
        context = {"article":article,"article_post_form":article_post_form,"columns":columns,
                   "tags":",".join([x for x in article.tags.names()]),}
        # 响应到："修改"文章的模板中
        return render(request,"article/update.html",context)


# 新增：文章"点赞"计数 ——————"类视图:实现！
from django.views import View

class IncreaseLikesView(View):
    def post(self,request,*args,**kwargs):
        article = ArticlePost.objects.get(id=kwargs.get("id"))
        # 点赞数+1
        article.likes += 1
        article.save()
        return HttpResponse("success")

# 点赞：不要求用户登录、不能重复点赞，字段数值存数据库、
# 点赞校验数据：存在浏览器的"LocalStorage中"，即通过判断当前"浏览器"是否赞过，而不是用户！
# 浏览器LocalStorage={2:"true",5:"true"}，即文章id2、id5，都被该"浏览器"赞过！
