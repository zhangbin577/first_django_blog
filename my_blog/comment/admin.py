from django.contrib import admin

# Register your models here.

# 将文章"评论"model注册到后台：测试"django-ckeditor"富文本编辑器！————————后台使用"Ckeditor"！
from .models import Comment

admin.site.register(Comment)

