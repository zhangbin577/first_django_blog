
from django import forms
from .models import Comment


# Forms表单类：高级处理
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]  # 只需取body字段，生成控件即可
