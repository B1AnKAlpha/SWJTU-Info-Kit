import sys
import requests
from bs4 import BeautifulSoup
import ddddocr
import time
from typing import Tuple, List, Optional
from login import login

def query_student(session: requests.Session, keyword: str, query_type: str = "studentName", max_retries: int = 3) -> Tuple[List[tuple[str, str, str, str]], str]:
    query_url = 'http://jwc.swjtu.edu.cn/vatuu/PublicInfoQueryAction'
    captcha_url = 'http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG'
    ocr = ddddocr.DdddOcr(show_ad=False)

    for attempt in range(max_retries):
        error_reason = ""
        try:
            # 1. 获取验证码
            captcha_img_response = session.get(captcha_url, timeout=10)
            if 'image' not in captcha_img_response.headers.get('Content-Type', ''):
                error_reason = f"获取验证码失败 (非图片格式)。服务器响应:\n{captcha_img_response.text}"
                time.sleep(0.5)
                continue

            # 2. 识别验证码
            captcha_code = ocr.classification(captcha_img_response.content)
            if not captcha_code or len(captcha_code) != 4:
                error_reason = f"验证码识别失败 (结果: '{captcha_code}')"
                time.sleep(0.5)
                continue

            # 3. 提交查询
            form_data = {'setAction': 'queryStudent', 'selectType': query_type, 'keyword': keyword, 'ranstring': captcha_code}
            resp = session.post(query_url, data=form_data, timeout=10)
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 4. 解析结果
            if "验证码不正确" in resp.text:
                error_reason = f"验证码不正确。服务器响应:\n{resp.text}"
                time.sleep(0.5)
                continue
            if "本页面需要登录系统后才能使用" in resp.text:
                return [], f"会话无效或已过期。服务器响应:\n{resp.text}"
            
            result_tables = soup.find_all('table', class_='table_gray')
            if len(result_tables) < 2:
                return [], f"未找到结果表格 (可能是查询无匹配)。服务器响应:\n{resp.text}"

            rows = result_tables[1].find_all('tr')
            if len(rows) <= 1:
                return [], f"查询成功但无匹配数据。服务器响应:\n{resp.text}"

            results = []
            for row in rows[1:]:
                cells = [td.text.strip() for td in row.find_all('td')]
                if len(cells) >= 5:
                    results.append((cells[1], cells[2], cells[3], cells[4]))
            return results, "" # 成功

        except requests.exceptions.RequestException as e:
            error_reason = f"网络请求错误: {e}"
        except Exception as e:
            error_reason = f"未知错误: {e}"
        
        print(f"    - 尝试 {attempt + 1}/{max_retries} 失败: {error_reason}")
        time.sleep(1)

    return [], f"达到最大重试次数后仍然失败: {error_reason}"

def main():
    """主函数，用于直接运行脚本进行测试。"""
    print("--- 西南交通大学教务网学生信息查询测试 ---")
    try:
        username = "你的学号"
        password = "你的密码"
        session = login(username, password)
        print("登录成功！")
        
        student_name = "张三"
        print(f"\n正在查询姓名: {student_name}")
        infos, error = query_student(session, student_name)
        
        if error:
            print(f"查询失败:\n{error}")
        elif infos:
            print(f"查询到 {len(infos)} 个结果:")
            for info in infos:
                print(f"  学号={info[0]}, 姓名={info[1]}, 学院={info[2]}, 专业={info[3]}")
        else:
            print("查询成功，但未找到匹配信息。")

    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == '__main__':
    main()
