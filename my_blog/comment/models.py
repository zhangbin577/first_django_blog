from django.db import models


# Create your models here.
from django.contrib.auth.models import User
from article.models import ArticlePost

# 导入："django-ckeditor"富文本编辑库，丰富文章"评论"的书写
from ckeditor.fields import RichTextField
# 导入：#"django-mptt"(树形数据结构)，实现"多级"评论！
from mptt.models import MPTTModel,TreeForeignKey


# 博文的"评论" (1个"article"多条"comment"、1个"user"多条"comment")
class Comment(MPTTModel):  # 将'models.Model'替换为'MPTTModel'

    # 被评的文章 (related_name：指定反向引用时，1表里的字段名，替代默认1表里的的"comment_set")
    article = models.ForeignKey(ArticlePost,on_delete=models.CASCADE,related_name="comments")
    # 发评的用户 (同理)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")

    # 内容
    # body = models.TextField()，用库的富文本字段"RichTextField"
    body = RichTextField()

    # 时间
    created = models.DateTimeField(auto_now_add=True)

    # 新增：mptt树形结构
    parent = TreeForeignKey(
        'self',on_delete=models.CASCADE,null=True,blank=True,related_name="children"
    )
    # 新增：记录二级评论的外键，即回复给了"谁"
    reply_to = models.ForeignKey(
        User,on_delete=models.CASCADE,null=True,blank=True,related_name="replyers"
    )

    # 替换Meta为MPTTMeta
    # class Meta:
    #     ordering = ("created",)  # 降序是"['-created']"
    class MPTTMeta:
        order_insertion_by = ["created"]

    def __str__(self):
        return self.body[:20]  # 显示：取出评论前20个字！


# 模型：继承了"MPTTModel"，因此表里多了些用于树形算法的"新字段"(level、tree_id等)
# parent字段：是必须定义的，用于存储数据间的关系，不要修改！
# replay_to外键：用于存储"被评论人"
# 注意：多级评论，不是无限级数，这里最多2级，超过2级的重置为2级，然后再将实际"被评人"存在reply_to里。
