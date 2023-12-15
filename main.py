# -*- coding: utf-8 -*-
# @Author : 艾登科技
# @Email : aidencaptcha@gmail.com
# @Address : https://github.com/aidencaptcha

# HuzhanSpider

# GeetestCaptchaBreak 【互站网-登录/注册案例】 案例

# api 地址

# * [GeetestCaptchaBreak](https://github.com/aidencaptcha/GeetestCaptchaBreak)

# 有需求请在邮箱联系

# aidencaptcha@gmail.com


# TODO: 名词解释/字段说明
# gt
# 验证ID。32位字符串, 验证码的唯一标识, 对公众可见, 用以区分不同页面的验证模块。gt在极验后台创建获得, 极验在每个验证场景部署不同的验证ID。
# 这里以【互站网-登录/注册】为案例 https://www.huzhan.com/
# gt = "c6f0e9eea7eebeb6dca9089a8adadecb"

# token
# 付费用户获取 艾登科技 的授权令牌
#  "token": "************"

# proxy
# 代理格式说明:
# "http://ip:port", # http代理, 无密码
# "http://user:pass@ip:port", # http代理, 有密码
# "http://www.xxx.com:port", # 隧道代理
# "socks5://user:pass@ip:port" # socks代理, 有密码
# 总结: 只要是 requests, scrapy 请求库支持的代理格式都可以
# proxy = "http://127.0.0.1:8888"


import json
import time
import requests
from loguru import logger


# 安装 python 第三方依赖
# pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/


logger.debug(r"""
    _     _      _                ____                _          _
   / \   (_)  __| |  ___  _ __   / ___|  __ _  _ __  | |_   ___ | |__    __ _ 
  / _ \  | | / _` | / _ \| '_ \ | |     / _` || '_ \ | __| / __|| '_ \  / _` |
 / ___ \ | || (_| ||  __/| | | || |___ | (_| || |_) || |_ | (__ | | | || (_| |
/_/   \_\|_| \__,_| \___||_| |_| \____| \__,_|| .__/  \__| \___||_| |_| \__,_|
                                              |_|
@Author : 艾登科技
@Email : aidencaptcha@gmail.com
@Address : https://github.com/aidencaptcha
@Description : API需求请在邮箱联系 aidencaptcha@gmail.com
""")


def main(proxy, token):
    """ Geetest3CaptchaBreak 【互站网-登录/注册】案例 """

    # TODO: 请求1.前端业务请求一-获取 gt 和 challenge
    huzhan_url = f"https://my.huzhan.com/html/StartCaptchaServlet?t={int(time.time()*1000)}"
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }
    response = requests.request("GET", huzhan_url, headers=headers)
    # response = requests.request("GET", url, headers=headers, proxies={"all": proxy}) # 业务请求是否使用代理
    # gt 和 challenge
    gt = json.loads(response.text).get("gt")
    challenge = json.loads(response.text).get("challenge")
    # 获取 cookie 中的 ci_session
    ci_session = response.cookies.get_dict()["ci_session"]


    # TODO: 请求2 -- 艾登科技API
    api_url = "http://x.x.x.x:x/xxx"
    headers = {
        "Connection": "close",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "gt": gt,
        "challenge": challenge,
        "proxy": proxy,
        "token": token
    })
    response = requests.request("POST", api_url, data=payload, headers=headers, timeout=30)

    # 解析 艾登科技API 返回响应
    res_json = json.loads(response.text)
    # 解析 艾登科技API 返回响应的 result
    result = res_json["result"]

    logger.debug(f"艾登科技API 返回响应：{res_json}")

    # 是否请求成功？
    if res_json["succ"] != 1:
        logger.debug("艾登科技API, 请求失败, 请联系技术")
        return

    # result 是否为 ""？ 若是则是推入消费队列操作，可忽略
    if result == "":
        logger.debug(f'任务已推入消费队列, 等待被消费, 当前任务数: {res_json["count"]}, 当前队列积压数: {res_json["reply"]-1}')
        return

    # err_msg 是否为 ""？ 若不是统一当异常处理，可忽略
    err_msg = result["err_msg"]
    if err_msg:
        return

    # 解析 艾登科技API 返回响应的 data
    data = res_json["result"]["data"]

    # 提取极验令牌
    # validate 是否存在？ 若是则是代表获取极验令牌失败，可能是遇到风控，高危/forbidden/ip封禁问题
    validate = data.get("validate")
    if not data.get("validate"):
        return

    gt = data["gt"]
    challenge_34 = data["challenge_34"]
    user_agent = res_json["result"]["user_agent"]
    # proxy = res_json["result"]["proxy"] # 业务请求是否使用代理

    # TODO: 请求3-前端业务请求二-账号登录
    # 根据获取到的令牌, 进行前端业务请求
    login_url = "https://my.huzhan.com/aform/index/login"
    # 你的账号密码
    login_name = "xxx"
    login_pass = "xxx"
    payload = f"login_name={login_name}&login_pass={login_pass}&login_phone=&vcode=&geetest_challenge={challenge_34}&geetest_validate={validate}&geetest_seccode={validate}%7Cjordan&scene=&login=name&random=1&action=login&passkey=1&RememberMe=1"
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '"Chromium";v="21", " Not;A Brand";v="99"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': user_agent,
        'sec-ch-ua-platform': '"Windows"',
        'Origin': 'https://my.huzhan.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://my.huzhan.com/html/login?c=',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8'
    }
    login_cookies = {"ci_session": ci_session}
    response = requests.request("POST", login_url, headers=headers, cookies=login_cookies, data=payload)
    # response = requests.request("POST", login_url, headers=headers, cookies=login_cookies, data=payload, proxies={"all": proxy}) # 业务请求是否使用代理
    logger.debug(response.cookies.get_dict())
    logger.debug(response.text)

    # 是否登录成功
    if json.loads(response.text).get("state") != 1:
        return

    return {
        'gt': gt,
        'challenge_34': challenge_34,
        'validate': validate,
        'cookies': response.cookies.get_dict()
    }


if __name__ == '__main__':
    proxy = "http://127.0.0.1:7890"
    token = "xxxxxx"

    count = 0
    for i in range(100):
        res = main(proxy, token)
        if not res:
            continue
        logger.debug(f"GeetestCaptchaBreak 极验三代【互站网-登录/注册】案例 gt: {res['gt'][:10]}..., 极验令牌：{res['validate'][:10]}..., 登录后的cookies: {str(res['cookies'])[:30]}..., 使用次数: {count+1}")
        count += 1
        # 速度限制, 防止风控
        time.sleep(2)
