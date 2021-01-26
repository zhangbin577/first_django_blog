from django.shortcuts import render,redirect

# Create your views here.
# 用户管理：登录、退出、注册、删除

# 导入：Django自带的登录验证模块
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .forms import UserLoginForm,UserRegisterForm


# 用户登录：
def user_login(request):
    if request.method == "POST":
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data
            # 检验：账号-密码是否正确，匹配数据库中的已有用户 (匹配到就返回该user对象)
            user = authenticate(username=data["username"],password=data["password"])
            if user:
                # 登录：并将数据存在session中，绑定当前的"request"和"user"
                login(request,user)
                # 登录后，返回到文章"列表页"
                return redirect("article:article_list")
            # 无user：为"空"，
            else:
                return HttpResponse("账号或密码输入有误，请重新输入！")
        else:
            return HttpResponse("账号或密码输入不合法！(与登录表单类不符合)")
    elif request.method == "GET":
        user_login_form = UserLoginForm()
        context = {"form":user_login_form}
        return render(request,"userprofile/login.html",context)
    else:
        return HttpResponse("请使用'GET/POST'请求数据！")


# 用户退出(登出)：也用Django自带的，直接auth的第3个兄弟"auth.logout()"
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 用户注册：
def user_register(request):
    if request.method == "POST":
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            # 设置：密码
            new_user.set_password(user_register_form.cleaned_data["password"])
            # 保存数据
            new_user.save()
            # 注册成功后，登录。
            login(request,new_user)
            # 返回到博客"列表页"。
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单有误，请重新输入！")
    elif request.method == "GET":
        user_register_form = UserRegisterForm()
        context = {"form":user_register_form}
        return render(request,"userprofile/register.html",context)
    else:
        return HttpResponse("请使用'GET/POST'请求数据")


from django.contrib.auth.models import User
# 引入：验证登录的"装饰器"
from django.contrib.auth.decorators import login_required

# 用户删除：前提"必须是登录用户、且是本用户" ——————安全！！
# 装饰器：要求调用user_delete()函数时，用户必须已登录；
# 若未登录则不执行此函数，将页面重定向到"/userprofile/login/"地址去。
@login_required(login_url="/userprofile/login/")
def user_delete(request,id):
    if request.method == "POST":
        user = User.objects.get(id=id)
        # 验证：删除操作的人，是否是当前登录的用户本人
        if request.user == user:
            # 是本人：退出登录、删除数据
            logout(request)
            user.delete()
            # 返回：到博客文章"列表页"
            return redirect("article:article_list")
        else:
            return HttpResponse("抱歉：您没有删除操作的权限！")
    else:
        return HttpResponse("仅接受post请求！")


from .forms import ProfileForm
from .models import Profile

# 编辑：用户信息 ——————：# 未登录不执行此函数，将页面重定向到"/userprofile/login/"地址去。
@login_required(login_url='/userprofile/login/')
def profile_edit(request,id):
    user = User.objects.get(id=id)
    # user_id：是外键自动生的字段，表两个表的关联
    # profile = Profile.objects.get(user_id=id) ——————注释：掉旧代码！

    # 修改：让"Profile表"根据是否已经存在，而动态的创建、获取
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:  # 不存在，就创建
        profile = Profile.objects.create(user=user)  # 见Django-orm的增加数据操作！

    if request.method == "POST":
        # 验证：修改数据者，是否为本人
        if request.user != user:
            return HttpResponse("亲,你无权限修改此用户信息哦！")

        # 上传的头像文件：是存在"request.FILES"中，参数传递给表单类
        profile_form = ProfileForm(request.POST,request.FILES)  # 修改本行：上传的用户头像处理
        if profile_form.is_valid():
            # 取出：清洗后的数据
            profile_cd = profile_form.cleaned_data
            # 重新：编辑赋值，保存进数据库
            profile.phone = profile_cd["phone"]
            profile.bio = profile_cd["bio"]
            # 若：request.FILES中有头像文件，则赋值保存
            if "avatar" in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 返回到，修改后的"编辑页"
            return redirect("userprofile:edit",id=id)
        else:
            return HttpResponse("注册表单输入有误，请重新输入~")
    elif request.method == "GET":
        context = {"user":user,"profile":profile}
        return render(request,"userprofile/edit.html",context)
    else:
        return HttpResponse("亲,请使用get/post请求数据！")

# request.FILES属性：表单上传的文件对象，是存储在类字典对象request.FILES中的，因此要修改表单类参数，将它也传入进去！
