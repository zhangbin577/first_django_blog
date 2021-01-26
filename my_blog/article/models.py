from django.db import models

# Create your models here.
# 导入内建的User()模型
from django.contrib.auth.models import User
# timezone：用于处理时间相关的事务
from django.utils import timezone
from django.urls import reverse
# Django-taggit：第三方库,文章"标签"
from taggit.managers import TaggableManager
# 文章"标题图"处理
from PIL import Image


# 新增：文章"栏目"，对文章"分类"
class ArticleColumn(models.Model):
    # 栏目标题(名称：Java、Django、测试、HTML等"栏目名")
    title = models.CharField(max_length=100,blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


# 博客文章：——————修改：增加文章"浏览量"字段、新增"点赞"计数
class ArticlePost(models.Model):
    # 作者 (on_delete=models.CASCADE代表的是当关联表中的数据删除时，该外键也删除)
    # blog文章的作者Author关联网站用户User  ——————：Djano2.0版本后外键里必设置"on_delete"
    author = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="作者")

    # 增加：文章"栏目"1对多的外键（blank=True,null=True：即无论"库/表单"，文章可以无"栏目值"，直接"保存/提交"）
    column = models.ForeignKey(ArticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name="article")

    # 增加：文章"标签"，引用库中的"TaggableManager"——————：1个处理多对多关系的管理器！
    tags = TaggableManager(blank=True)

    # 增加：文章"标题图"
    avatar = models.ImageField(upload_to="article/%Y%m%d",blank=True)

    # 标题
    title = models.CharField(max_length=100,verbose_name="标题")
    # 正文
    body = models.TextField(verbose_name="正文")
    # 创建时间  (=timezone.now，即创建数据时，默认写入当前日期时间)
    created = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    # 更新时间  (=True,即每次数据更新时，自动写入当前日期时间)
    updated = models.DateTimeField(auto_now=True,verbose_name="更新时间")

    # 增加：文章"浏览量"字段 ——————PositiveIntegerField：是存储正整数的字段！
    total_views = models.PositiveIntegerField(default=0)

    # 新增：点赞数统计
    likes = models.PositiveIntegerField(default=0)


    # 保存时：处理文章"标题图"图片
    # save()：是model内置的方法，会在model实例每次保存时调用，这里"重写"它，加入"图片处理"的逻辑！
    def save(self,*args,**kwargs):
        # 调用：父类原有的save()方法，即将model中字段数据，保存进数据库中
        # 因为：图片处理，是基于已经保存的图片——————即：这句一定要在处理图片之前执行！
        article = super(ArticlePost,self).save(*args,**kwargs)

        # 标题图处理：缩放图片大小
        # 判断：是否有标题图 and 排除掉article_detail()统计"浏览量"时调用的"save(update_fields=['total_views'])"
        # 免得：每次进入文章"详情页"，都要处理"标题图"，太影响性能！
        if self.avatar and not kwargs.get("update_fields"):
            # 打开：原图对象，获取它的"分辨率"
            image = Image.open(self.avatar)
            (x,y) = image.size
            # 新图：固定宽度400，根据原图比例得到高度
            new_x = 400
            new_y = int(new_x*(y/x))
            # 用新图：覆盖掉原图即可，Image.ANTIALIAS表示缩放采用"平滑滤波"
            resized_image = image.resize((new_x,new_y),Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        # 最后：将原有父类save()返回结果，原封不动的返回去
        return article


    def __str__(self):
        return self.title  # 后台中：作为对象的显示值

    # 内部类：提供模型的"元数据" ——————即：任何非字段的数据！(来帮助理解，规范类的行为)
    class Meta:
        db_table = "article"
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ("-created",)  # 保证：取文章list[]时，新文章永远在最顶部位置。

    # 获取文章地址(post_comment中用)
    def get_absolute_url(self):
        # 通过reverse()方法，返回文章"详情页"的url，实现路由重定向
        return reverse("article:article_detail",args=[self.id])


    # 新增：有bug的方法，用于Blog自动化测试 ——————该方法：用作判断文章是否为"最近发布"！
    def was_created_recently(self):
        # 若是"最近"发表的，则返回"True"
        diff = timezone.now() - self.created

        # 修正bug：通过测试找到了bug
        # if diff.days<=0 and diff.seconds<60:
        #     return True
        if diff.days==0 and diff.seconds>=0 and diff.seconds<60:
            return True
        else:
            return False

