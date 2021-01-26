
# 用户登录：需填写的账号密码表单数据

# 引入：forms表单类
from django import forms
# 引入：内置的User模型
from django.contrib.auth.models import User


# 用户：登录表单
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


# 用户：注册表单
class UserRegisterForm(forms.ModelForm):
    # 覆写掉：User的"password"字段，以便我们自己进行数据的验证工作
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        # 继承的User模型中的password字段就没了，已经被上面覆写掉了！
        fields = ["username","email"]

    # 对2次密码：是否一致进行检查
    # def clean_[字段]：这种写法Django会自动调用，来对单个字段的数据进行验证清洗。
    def clean_password2(self):
        data = self.cleaned_data
        if data.get("password") == data.get("password2"):
            return data.get("password")
        else:
            raise forms.ValidationError("两次输入不一致，请重试！")


# 注意：这里是"clean_password2()"，不然会导致password2被Django判定为无效数据而清洗掉，
# 从而password2属性不存在。最终导致两次密码输入始终会不一致，并且很难判断出错误原因。

# 自定义验证：Django中使用"def clean()"方法，对表单中的数据进行验证。(对某个字段，进行自定义的验证)
# 方式：定义1个方法，方法名规则是"clean_fieldname"，若验证失败，就抛出1个验证错误"ValidationError()"。
# 若需要针对多个字段进行验证，那么可以重写 clean 方法


from .models import Profile  # 引入：Profile模型


# 扩展：用户信息的"表单类"
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone","avatar","bio"]


