import requests
import json
import time
import ddddocr

def login(username: str, password: str) -> requests.Session:
    """Logs into the SWJTU JWC and returns an authenticated session."""
    session = requests.Session()
    ocr = ddddocr.DdddOcr(show_ad=False)

    login_page_url = 'http://jwc.swjtu.edu.cn/service/login.html'
    session.get(login_page_url)

    captcha_url = 'http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG'
    captcha_img = session.get(captcha_url).content
    captcha_code = ocr.classification(captcha_img)
    print(f"自动识别验证码为: {captcha_code}")

    login_action_url = 'http://jwc.swjtu.edu.cn/vatuu/UserLoginAction'
    login_data = {
        'username': username,
        'password': password,
        'ranstring': captcha_code,
        'url': '',
        'returnType': '',
        'returnUrl': '',
        'area': '',
    }
    
    headers = {
        'Referer': login_page_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    
    response = session.post(login_action_url, data=login_data, headers=headers)
    
    if response.status_code != 200:
        raise ConnectionError("无法连接到登录服务器。")

    try:
        login_status = response.json()
        if login_status.get('loginStatus') != '1':
            raise ValueError(f"登录失败: {login_status.get('loginMsg', '未知错误')}")
    except (requests.exceptions.JSONDecodeError, ValueError) as e:
        print("无法解析登录响应。登录页面可能已更改。")
        print("--- 服务器响应 ---")
        print(response.text)
        print("--- 服务器响应结束 ---")
        raise

    return session
