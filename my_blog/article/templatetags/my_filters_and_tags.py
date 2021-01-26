
# 自定义模板"过滤器和标签"
from django import template

register = template.Library()


# 写"过滤器"
@register.filter(name="transfer")
def transfer(value,arg):
    """实现：将输出,强制转换为字符串'arg'"""
    return arg


@register.filter()
def lower(value):
    """实现：将字符串，转换为小写字符"""
    return value.lower()


# 调用的方式：任意模板中{% load my_filters_and_tags %}
# {{ "ZB"|transfer:'cool' }}  ='cool'
# {{ "ZB"|lower }}  ='zb'


# 正式开始：写个显示"相对日期"的过滤器！
# bolg发布：具体的时间，并不好看，不如"发表于3天前、发表于2019年"等相对时间好看

from django.utils import timezone
import math

# 获取相对时间
@register.filter(name="timesince_zh")
def time_since_zh(value):
    now = timezone.now()
    # diff = 当前UTC时间-文章发布时间
    diff = now - value

    if diff.days==0 and diff.seconds>=0 and diff.seconds<60:
        return "刚刚"
    if diff.days==0 and diff.seconds>=60 and diff.seconds<3600:
        return str(math.floor(diff.seconds/60))+"分钟前"   # 60分钟
    if diff.days==0 and diff.seconds>=3600 and diff.seconds<86400:  # 24h
        return str(math.floor(diff.seconds/3600))+"小时前"
    if 1 <= diff.days < 30:
        return str(diff.days)+"天前"
    if 30 <= diff.days < 365:
        return str(math.floor(diff.days/30))+"月前"
    if diff.days >= 365:
        return str(math.floor(diff.days/365))+"年前"


# 写"标签"：简单标签\包含标签
@register.simple_tag
def change_http_to_https(url):
    new_url = url.replace("http://","https://")
    return new_url
# 调用的方式：任意模板中{% load my_filters_and_tags %}
# {{ change.._https 'url1' }}  ='https://127.0.0.1:8000/index'

# 包含标签：用法类似！
