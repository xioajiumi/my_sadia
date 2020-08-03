#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 16:17
# @Author  : Aries
# @Site    : 
# @File    : e_validate.py
# @Software: PyCharm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


def validate(receiver, code,):

    receiver = receiver  # 收件人邮箱
    code = code  # 验证码

    # E-Authenticatecode   SXDCVVWMKJBUWLMY
    smtpserver = 'smtp.163.com'
    username = 'sadia_server@163.com'
    password = 'SXDCVVWMKJBUWLMY'
    sender = username  # sender一般要与username一样

    subject = '注册验证邮件，请勿回复'
    subject = Header(subject, 'utf-8').encode()

    # 构造邮件对象MIMEMultipart对象
    # 主题，发件人，收件人等显示在邮件页面上的。
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'SADIA'
    msg['To'] = receiver

    # 构造文字内容
    text = "Hi` 欢迎使用SADIA!\n这是您的验证码：" + code
    text_plain = MIMEText(text, 'plain', 'utf-8')
    msg.attach(text_plain)

    # 发送邮件
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    # 用set_debuglevel(1)可以打印出和SMTP服务器交互的所有信息。
    # smtp.set_debuglevel(1)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
