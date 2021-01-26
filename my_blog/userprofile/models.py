from django.db import models


# Create your models here.
# 扩展"用户信息"：自带的User模型，字段少的可怜，添上"电话号、头像"(用模型"1对1关联"的方法)

from django.contrib.auth.models import User
# 引入：内置信号"post_save"
# from django.db.models.signals import post_save ——————信号实现"User和Profile"同步创建的"bug修复"
# 引入：信号接收器receiver的"装饰器"
# from django.dispatch import receiver


# 扩展：用户信息
class Profile(models.Model):
    # 与User模型：构成"1对1"关联                                # 反向操作时的字段名，代替"_set"
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    # 电话号
    phone = models.CharField(max_length=20,blank=True)
    # 头像："%Y%m%d"是日期格式化的写法，最终格式化为"系统时间"
    avatar = models.ImageField(upload_to="avatar/%Y%m%d",blank=True)
    # 个人简介
    bio = models.TextField(max_length=500,blank=True)
    # blank和null的区别：null是数据库的范围，而blank是用于验证。若1个字段的blank=True,
    # Django进行表单数据验证时，会允许该字段是空值。

    def __str__(self):
        return "user {}".format(self.user.username)


# 信号接收函数(信号,sender=发送者)：——————新建User实例时，会自动调用！
# @receiver(post_save,sender=User)
# def create_user_profile(sender,instance,created,**kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# # 信号接收函数：——————更新User实例时，会自动调用！
# @receiver(post_save,sender=User)
# def save_user_profile(sender,instance,**kwargs):
#     instance.profile.save()

# Django的信号机制："sender-->post_save信号-->receiver"，这里当模型调用.save()方法保存入库后触发
# 接收函数()：实现了每当"User"创建/更新时，发送"信号"启动def()函数，使"Profile"也自动的创建/更新。
# 为什么：删除User表不需要信号？
# 答案是：两者的关系采用了models.CASCADE级联删除，已经带有关联删除的功能了。
# 当然：可以不使用信号来自动创建Profile()表，而采用手动方式实现。


# 注意：建好做makemigrations-migraet后，还不能直接admin登录"lenovo"，会报错！！！
# 因为：之前建的User数据都没有对应的Profile模型，违背了现有的模型。
# 1种解决办法：是干脆删除旧的数据，因此就需用到Django的shell命令。——————：python manage.py shell进入shell！
# shell下>>>：删除User数据库，此时级联的article模型库也会删除，相关文章也没了！
# 命令：from django.contrib.auth.models import User、User.objects.all().delete()
# 此时：再"select * from auth_user/article；——————：=Empty set (0.00 sec)"为空！
# 删完：重新"createsuperuser"，建管理员账户。

# BUG修复：信号实现"User和Profile"同步创建，会产生bug，因此注释掉！！！
