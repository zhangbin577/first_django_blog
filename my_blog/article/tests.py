from django.test import TestCase

# Create your tests here.

# 个人博客网站开发：自动化测试，人工测试就是每次的"runserver"太麻烦！
# 单元测试(unit testing)：是指对软件中的最小可测试单元进行检查和验证。总的来说，单元就是人为规定的最小的被测功能模块。
# 为解决"人工测试"的种种问题，Django的"test"引入了Python的单元测试模块"unittest"
# unittest库：是python自带的标准单元测试库，无需安装。因为python语言一切皆对象，故而最小"单元"可是“函数/类/模块”。

import datetime
from django.utils import timezone  # timezone：用于处理时间相关的事务
from article.models import ArticlePost
from django.contrib.auth.models import User


# 文章模型M的测试：
# 通过4个"测试"方法，更全面的测试"was_created_recently()"方法，
# 确保它对于"过去/最近/将来"的3种情况，都能返回正确的值。——————证实：该"功能"方法是没bug的，可以不用修改完善！
class ArticlePostModelTests(TestCase):
    def test_was_created_recently_with_future_article(self):
        # 若文章创建时间为未来30天，返回False
        author = User(username="user",password="test_password")
        author.save()
        # 创建1篇：未来30后发布的文章（30天后的时间获取方式"created=..."）
        future_article = ArticlePost(author=author,title="test",body="test",
                                     created=timezone.now()+datetime.timedelta(days=30))
        # python单元测试库的"断言"方法：作用，检测方法内2个参数是否"一致"，不一致则抛异常提示！
        self.assertIs(future_article.was_created_recently(),False)

    def test_was_created_recently_with_seconds_before_article(self):
        # 若文章创建时间为1分钟内，返回True ——————它才是算是最近发布的！
        author = User(username="user1",password="test_password")
        author.save()
        seconds_before_article = ArticlePost(author=author,title="test1",body="test1",
                                             created=timezone.now()-datetime.timedelta(seconds=45))
        self.assertIs(seconds_before_article.was_created_recently(),True)

    def test_was_created_recently_with_hours_before_article(self):
        # 若创建文章的时间为3hours前，返回False
        author = User(username="user2",password="test_password")
        author.save()
        hours_before_article = ArticlePost(author=author,title="test2",body="test2",
                                           created=timezone.now()-datetime.timedelta(hours=3))
        self.assertIs(hours_before_article.was_created_recently(),False)

    def test_was_created_recently_with_days_before_article(self):
        # 若文章创建时间为5天，返回False
        author = User(username="user3",password="test_password")
        author.save()
        days_before_article = ArticlePost(author=author,title="test3",body="test3",
                                          created=timezone.now()-datetime.timedelta(days=5))
        self.assertIs(days_before_article.was_created_recently(),False)


# 文章视图V的测试
# 测试：文章"浏览量"统计，潜在的bug（如：增加的浏览量，未能正常保存进数据库、updated字段也错误的一并更新）
from time import sleep
from django.urls import reverse


class ArticlePostViewTests(TestCase):
    def test_increase_views(self):
        # 请求详情视图时，阅读量+1("0->1")
        author = User(username="user4",password="test_password")
        author.save()
        article = ArticlePost(author=author,title="test4",body="test4")
        article.save()
        self.assertIs(article.total_views,0)         # 新文章=0

        url = reverse("article:article_detail",args=(article.id,))
        response = self.client.get(url)

        viewed_article = ArticlePost.objects.get(id=article.id)
        self.assertIs(viewed_article.total_views,1)  # 访问了=1

    def test_increase_views_but_not_change_updated_field(self):
        # 请求详情视图时，不改变updated字段！
        author = User(username="user5",password="test_password")
        author.save()
        article = ArticlePost(author=author,title="test5",body="test5")
        article.save()

        sleep(0.5)
        url = reverse("article:article_detail",args=(article.id,))
        response = self.client.get(url)

        viewed_article = ArticlePost.objects.get(id=article.id)
        self.assertIs(viewed_article.updated - viewed_article.created < timezone.timedelta(seconds=0.1),True)

    # 这两个测试方法：通过了，证实"view.py"中的"total_views、updated"的代码没问题！


# 学完测试：接着学习"日志"，"记录"程序的错误等信息！
# 日志：指程序在运行过程中。对状态、时间、错误等信息的记录，
# 即把运行过程中产生的信息输出保存起来，功开发者查阅！
