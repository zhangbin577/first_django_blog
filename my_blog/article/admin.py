from django.contrib import admin

# Register your models here.
from .models import ArticlePost

admin.site.register(ArticlePost)


from .models import ArticleColumn
# 注册：文章"栏目"
admin.site.register(ArticleColumn)
