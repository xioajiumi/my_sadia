import smtplib
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageDraw, ImageFont
from random import randint
from io import BytesIO
from app01.bbdforms import RegForm
from app01 import models
from bs4 import BeautifulSoup
from .e_validate import validate
from .my_decorator import stop_get, need_login


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.is_ajax():
        response = {'code': 100, 'msg': None}
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        code = request.POST.get('code')
        if request.session['valid_code'].upper() == code.upper():
            user = auth.authenticate(request, username=name, password=pwd)
            if user:
                response['msg'] = "登陆成功"
                auth.login(request, user)
            else:
                response['code'] = 101
                response['msg'] = "用户名或密码错误"
        else:
            response['code'] = 102
            response['msg'] = "验证码错误啊啊啊啊啊啊啊"
        return JsonResponse(response)


def get_random_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))


def get_random_code(digit=4):
    code = ''
    for i in range(digit):
        code += str(randint(0, 9))
    return code


def get_code(request):
    img = Image.new('RGB', (200, 40), get_random_color())
    my_font = ImageFont.truetype('static/font/yujian.ttf', 34)
    draw = ImageDraw.Draw(img)
    valid_code = ''
    for i in range(5):
        num = str(randint(0, 9))
        up_chr = str(chr(randint(65, 90)))
        lower_chr = str(chr(randint(97, 122)))
        code = [num, up_chr, lower_chr][randint(0, 2)]
        valid_code += code
        draw.text((30 + i * 30, randint(-1, 1) * 10), code, font=my_font)
    request.session['valid_code'] = valid_code
    # 在图片上画线
    #     draw.line((x1,y1,x2,y2),fill=get_random_color())
    #
    # for i in range(100):
    #     # 画点
    #     draw.point([random.randint(0,width),random.randint(0,height)],fill=get_random_color())
    #     x = random.randint(0,width)
    #     y = random.randint(0,height)
    #     # 画弧形
    #     draw.arc((x,y,x+4,y+4),0,90,fill=get_random_color())
    f = BytesIO()
    img.save(f, 'png')
    return HttpResponse(f.getvalue())
    # response = {'code': 100, 'msg': None}
    # return JsonResponse(response)


def index(request):
    # # return HttpResponse('hello world')
    # data = {'name': 'zahngsan', 'age': 20, 'sex': '男'}
    # return JsonResponse(data, safe=False)
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {'article_list': article_list})


@stop_get
def e_validate(request):
    result = {'state': 'error', 'data': ''}
    if request.method == 'POST':
        # 1.获取邮箱
        email_name = request.POST.get('email')
        if email_name:
            # 2.向邮箱发送邮件
            try:
                code = get_random_code()
                request.session['code'] = code
                validate(email_name, code)
            except Exception as e:
                result['data'] = str(e)
            else:
                """将内容保存到数据库"""
                result['data'] = 'success'
                result['state'] = 'success'
            finally:
                # 3.保存到数据库
                return JsonResponse(result)
    # 如果没有进入if，就重定向到 邮箱注册页面
    return redirect('/register/')


def register(request):
    if request.method == 'GET':
        form = RegForm()
        return render(request, 'register.html', {'form': form})
    elif request.is_ajax():
        response = {'code': 100, 'msg': None}
        form = RegForm(request.POST)
        if form.is_valid():
            code = request.POST.get('code')
            if code == request.session['code']:
                clean_data = form.cleaned_data
                clean_data.pop('re_pwd')
                avatar = request.FILES.get('avatar')
                if avatar:
                    clean_data['avatar'] = avatar
                user = models.UserInfo.objects.create_user(**clean_data)
                if user:
                    response['msg'] = '创建成功'
                else:
                    response['code'] = 103
                    response['msg'] = '创建失败'
            else:
                response['code'] = 102
                response['msg'] = "验证码错误"

        else:
            response['code'] = 101
            response['msg'] = form.errors
        return JsonResponse(response, safe=False)


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def site_page(request, username, *args, **kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')

    blog = user.blog
    article_list = blog.article_set.all()
    condition = kwargs.get('condition')
    param = kwargs.get('param')
    if condition == 'tag':
        article_list = article_list.filter(tag=param)
    elif condition == 'category':
        article_list = article_list.filter(category_id=param)
    elif condition == 'archive':
        year_t = param.split('-')
        article_list = article_list.filter(create_time__year=year_t[0], create_time__month=year_t[1])

    category_ret = models.Category.objects.all().filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')
    tag_ret = models.Tag.objects.all().filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')
    year_ret = models.Article.objects.all().filter(blog=blog).annotate(
        month=TruncMonth('create_time')).values('month').annotate(
        c=Count('nid')).values_list('month', 'c')

    return render(request, 'site_page.html', locals())


def article_detail(request, username, pk):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    category_ret = models.Category.objects.all().filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')
    tag_ret = models.Tag.objects.all().filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')
    year_ret = models.Article.objects.all().filter(blog=blog).annotate(
        month=TruncMonth('create_time')).values('month').annotate(
        c=Count('nid')).values_list('month', 'c')
    article = models.Article.objects.all().filter(nid=pk).first()
    # commit_list = article.commit_set.all()
    return render(request, 'article_detail.html', locals())


def diggit(request):
    response = {'code': 100, 'msg': None}
    if request.user.is_authenticated:
        user_id = request.user.pk
        is_up = request.POST.get("is_up")
        # is_up = load(is_up)
        if is_up == 'true':
            is_up = True
        else:
            is_up = False
        article_id = request.POST.get("article_id")
        up_ret = models.UpAndDown.objects.filter(user_id=user_id, article_id=article_id).first()
        if up_ret:
            response['code'] = 102
            response['msg'] = '您已点过啦'
        else:
            from django.db import transaction
            with transaction.atomic():
                models.UpAndDown.objects.create(article_id=article_id, user_id=user_id, is_up=is_up)
                if is_up:
                    models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                    response['msg'] = '点赞成功'
                else:
                    models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                    response['msg'] = '点踩成功'
    else:
        response['code'] = 101
        response['msg'] = '请先登录'
    return JsonResponse(response, safe=False)


@need_login
@stop_get
def commit(request):
    response = {'code': 100, 'msg': None}
    if request.user.is_authenticated:
        user_id = request.user.pk
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.delete()

        with transaction.atomic():
            ret = models.Commit.objects.create(
                article_id=article_id, content=str(soup), user_id=user_id, parent_id=parent_id)
            print(ret)
            models.Article.objects.filter(pk=article_id).update(commit_num=F('commit_num') + 1)
            if parent_id:
                response['parent_name'] = ret.parent.user.username
            response['msg'] = '评论成功'
            response['username'] = ret.user.username
            response['reply_content'] = ret.content
    else:
        response['code'] = 101
        response['msg'] = '请先登录'
    return JsonResponse(response, safe=False)


@need_login
def home_backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    return render(request, 'backend/home_backend.html', locals())


@need_login
def add_article(request):
    if request.method == 'GET':
        return render(request, 'backend/add_article.html')
    else:
        title = request.POST.get('title')
        text_content = request.POST.get('text_content')
        soup = BeautifulSoup(text_content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.delete()
        desc = soup.text[0:150]
        models.Article.objects.create(
            title=title, desc=desc, content=str(soup), blog=request.user.blog)
        return redirect('/backend/')


@xframe_options_sameorigin
def upload(request):
    file = request.FILES.get('imgFile')
    response = {
        "error": 0,
        'url': '/media/file/' + file.name
    }
    file = request.FILES.get('imgFile')
    with open('media/file/' + file.name, 'wb') as f:
        for line in file:
            f.write(line)
    return JsonResponse(response, safe=False)


@stop_get
def search(request):
    search_info = request.POST.get('search_info')
    article_list = models.Article.objects.all()
    for each in article_list.all():
        if str(each) == search_info:
            id = each.pk
            searched_article_list = models.Article.objects.filter(nid=id)

            print(searched_article_list)

    return render(request, 'search.html', locals())


def start(request):
    return render(request, 'start.html')


@stop_get
def delete(request):
    article_id = request.POST.get('article_id')
    models.Article.objects.filter(pk=article_id).delete()
    response = {'code': 100, 'msg': '删除成功'}
    return JsonResponse(response)


def page_not_found(request):
    return render(request, 'error.html')


def test(request):
    return render(request, 'base.html')


def edit(request):
    return render(request, 'index.html', locals())
