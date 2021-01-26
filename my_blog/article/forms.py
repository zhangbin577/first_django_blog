
# 使用Django的Forms表单类，发表"新文章" ——————直接用"forms高级处理"！
# 即在"前端"：通过页面的表单，书写"文章标题、内容"等，提交数据到数据库
# 不再：每次都只能在"后台"，书写文章。

# forms高级处理：将"Models"实体类和"Forms"表单类，结合到一起使用。
# 即：做关联，表单的东西，来于实体类，实现"属性"的共享！


# 导入"表单类"
from django import forms
from .models import ArticlePost


# 文章的：表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ["title","body","tags","avatar"]  # 新增：添上文章"标签"字段、文章"标题图"

