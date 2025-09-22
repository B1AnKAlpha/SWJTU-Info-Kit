# 西南交通大学信息查询工具集

## 简介

本项目是一个基于 Python 的工具集，旨在方便地从西南交通大学（SWJTU）官方网站（如教务网）获取各类公开信息。项目通过模拟登录、接口请求和数据解析，实现信息查询的自动化。

目前已实现的功能是查询学生信息，未来计划扩展更多查询功能。

## 核心模块

- **统一登录 (`login.py`)**: 封装了通用的教务网登录逻辑，处理验证码识别，为其他查询模块提供经过身份验证的会话 (`requests.Session`)。
- **验证码识别**: 项目内置 `ddddocr` 库，用于自动识别图形验证码，实现无人值守操作。
- **错误处理与重试**: 查询脚本包含了网络请求失败和验证码错误的重试机制，提高了脚本的稳定性。

## 已实现功能

### 1. 学生信息查询 (`query_student_info.py`)

- **功能**: 根据学生姓名等关键词查询学生的公开基本信息（学号、姓名、学院、专业）。
- **依赖**: `login.py`

## 环境要求

在运行此脚本之前，请确保您已安装以下 Python 库：

- `requests`
- `beautifulsoup4`
- `ddddocr`

您可以使用 pip 来安装它们：
```bash
pip install requests beautifulsoup4 ddddocr
```

## 使用方法

### 学生信息查询

1.  **配置凭据**:
    在 `query_student_info.py` 的 `main` 函数中，你需要修改 `username` 和 `password` 变量为你自己的教务网账号和密码。

    ```python
    # query_student_info.py
    def main():
        try:
            username = "你的学号"  # <--- 修改这里
            password = "你的密码"  # <--- 修改这里
            session = login(username, password)
            # ...
    ```

2.  **运行查询**:
    直接运行 `query_student_info.py` 脚本即可进行测试。默认会查询姓名为“张三”的学生。

    ```bash
    python query_student_info.py
    ```

3.  **作为模块使用**:
    你也可以将 `login` 和 `query_student` 函数导入到你自己的项目中来使用。

    ```python
    from login import login
    from query_student_info import query_student

    try:
        # 登录
        my_session = login("你的学号", "你的密码")
        print("登录成功！")

        # 查询信息
        keyword = "李四"
        student_list, error_message = query_student(my_session, keyword)

        if error_message:
            print(f"查询出错: {error_message}")
        elif student_list:
            print(f"找到了 {len(student_list)} 个结果:")
            for student in student_list:
                print(f"学号: {student[0]}, 姓名: {student[1]}, 学院: {student[2]}, 专业: {student[3]}")
        else:
            print("没有找到匹配的学生。")

    except Exception as e:
        print(f"发生错误: {e}")
    ```

## 未来计划

- [ ] 查询课程信息
- [ ] 查询成绩信息
- [ ] 查询空闲教室
- [ ] ... (欢迎提出更多想法)

## 注意事项

- 本项目仅供学习和技术交流使用，请勿用于非法用途。
- 请妥善保管您的个人账号和密码，避免泄露。
- 各个网站的页面结构或接口可能会发生变化，届时脚本可能需要相应地进行更新。
