#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/23 0:11
# @Author  : Aries
# @Site    : 
# @File    : my_decorator.py
# @Software: PyCharm
from functools import wraps
from django.shortcuts import render, redirect


def stop_get(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        if request.method == 'GET':
            return render(request, 'error.html')
        else:
            return f(request, *args, **kwargs)

    return decorated


def need_login(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated:
            return f(request, *args, **kwargs)
        else:
            return redirect('/login/')

    return decorated
