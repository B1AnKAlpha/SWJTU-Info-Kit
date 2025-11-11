# 西南交通大学信息查询工具集

## 简介

本项目是一个基于 Python 的工具集，旨在方便地从西南交通大学（SWJTU）官方网站（如教务网）获取各类公开信息。项目通过模拟登录、接口请求和数据解析，实现信息查询的自动化。


## 已实现功能

### 1. 学生信息查询 (`query_student_info.py`)

- **功能**: 根据学生姓名等关键词查询学生的公开基本信息（学号、姓名、学院、专业）。
- **依赖**: `login.py`

### 2. 扬华素质网公示信息爬虫 (`yanghua_scraper.py`)

- **功能**: 爬取扬华素质网公示页面的学生名单信息（如奖助学金获得者名单），自动解析分页数据并保存为Excel文件。



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

### 扬华素质网公示信息爬虫

1.  **导入函数**:
    将 `scrape_student_list` 函数导入到你的项目中。

    ```python
    from yanghua_scraper import scrape_student_list
    ```

2.  **使用示例**:
    传入扬华素质网公示页面的URL即可爬取数据。

    ```python
    # 爬取单个公示页面
    url = 'http://xg.swjtu.edu.cn/web/Publicity/BursaryDetail?wz34zM3=xxx.shtml'
    df = scrape_student_list(url)
    
    if df is not None:
        print(f"成功爬取 {len(df)} 条记录")
        print(df.head())  # 查看前几条数据
    ```

3.  **批量爬取示例**:
    ```python
    from yanghua_scraper import scrape_student_list
    
    # 多个公示页面URL列表
    urls = [
        'http://xg.swjtu.edu.cn/web/Publicity/BursaryDetail?wz34zM3=url1.shtml',
        'http://xg.swjtu.edu.cn/web/Publicity/BursaryDetail?wz34zM3=url2.shtml',
        'http://xg.swjtu.edu.cn/web/Publicity/BursaryDetail?wz34zM3=url3.shtml'
    ]
    
    for url in urls:
        scrape_student_list(url)  # 自动保存为Excel文件
    ```



## 注意事项

- 本项目仅供学习和技术交流使用，请勿用于非法用途。
- 请妥善保管您的个人账号和密码，避免泄露。
- 各个网站的页面结构或接口可能会发生变化，届时脚本可能需要相应地进行更新。
