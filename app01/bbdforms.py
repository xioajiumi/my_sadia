#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/27 17:08
# @Author  : Aries
# @Site    : 
# @File    : bbdforms.py
# @Software: PyCharm
from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from app01 import models


class RegForm(forms.Form):
    username = forms.CharField(max_length=18, min_length=3, label='用户名',
                               error_messages={
                                 'max_length': '用户名过长',
                                 'min_length': '用户名过短',
                                 'required': '用户名不能为空'},
                               widget=widgets.TextInput(attrs={'class': 'form-control'}),
                               )
    password = forms.CharField(max_length=18, min_length=3, label='密码',
                               error_messages={
                                   'max_length': '密码过长',
                                   'min_length': '密码过短',
                                   'required': '密码不能为空'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                               )
    re_pwd = forms.CharField(max_length=18, min_length=3, label='确认密码',
                             error_messages={
                                 'max_length': '密码过长',
                                 'min_length': '密码过短',
                                 'required': '密码不能为空'},
                             widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                            )
    email = forms.EmailField(max_length=18, min_length=3, label='邮箱',
                             error_messages={
                                 'max_length': '邮箱过长',
                                 'min_length': '邮箱过短',
                                 'required': '邮箱不能为空'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}),
                             )

    # 局部钩子，局部校验
    def clean_username(self):
        name = self.cleaned_data.get('username')
        # if str(name).startswith('sb'):
        #     raise ValidationError('含有不合规开头')
        # else:
        #     return name
        user = models.UserInfo.objects.filter(username=name).first()
        if user:
            raise ValidationError('用户已存在')
        else:
            return name

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_pwd')

        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')
