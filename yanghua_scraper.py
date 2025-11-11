import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_page_data(url, headers):
    """获取单个页面的数据"""
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取页面标题
    title_tag = soup.find('title')
    page_title = title_tag.get_text(strip=True) if title_tag else '未知标题'
    
    table = soup.find('table')
    if not table:
        return None, None, None, page_title
    
    # 提取表头
    header_row = table.find('tr')
    table_headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])] if header_row else []
    if not table_headers:
        table_headers = ['序号', '姓名', '学号', '专业', '学院', '奖助学金名称']
    
    # 提取数据行
    data_rows = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            data_rows.append([col.get_text(strip=True) for col in cols])
    
    return data_rows, table_headers, soup, page_title


def get_pagination_info(soup):
    """获取分页信息"""
    page_box = soup.find('div', class_='page-box')
    if page_box:
        total_span = page_box.find('span', class_='text-num')
        if total_span:
            try:
                total_records = int(total_span.get_text(strip=True))
                return total_records, (total_records + 14) // 15
            except ValueError:
                pass
    return 0, 1


def get_order_id(soup):
    """从下一页链接中提取orderId"""
    page_box = soup.find('div', class_='page-box')
    if page_box:
        pagecell = page_box.find('ul', class_='pagecell')
        if pagecell:
            last_li = pagecell.find_all('li')[-1]
            a_tag = last_li.find('a')
            if a_tag and 'orderId=' in a_tag.get('href', ''):
                return a_tag['href'].split('orderId=')[1].split('&')[0]
    return None


def fetch_page(args):
    """多线程爬取单个页面"""
    page_num, url, headers = args
    try:
        data_rows, _, _, _ = get_page_data(url, headers)
        return page_num, data_rows
    except:
        return page_num, None


def scrape_student_list(url):
    """爬取学生名单并保存到Excel"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # 获取第一页，提取分页信息和标题
        data_rows, table_headers, soup, title = get_page_data(url, headers)
        if not data_rows:
            return None
        
        print(f"\n{'='*80}\n开始爬取: {title}\n{'='*80}")
        
        total_records, total_pages = get_pagination_info(soup)
        order_id = get_order_id(soup)
        
        if not order_id:
            print("错误: 无法提取orderId")
            return None
        
        print(f"总记录数: {total_records}, 总页数: {total_pages}")
        
        # 并行爬取所有页面
        base_url = 'http://xg.swjtu.edu.cn/web/Publicity/BursaryDetail'
        page_urls = [f"{base_url}?page={i}&orderId={order_id}" for i in range(1, total_pages + 1)]
        
        page_results = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            tasks = [(i + 1, page_urls[i], headers) for i in range(len(page_urls))]
            futures = [executor.submit(fetch_page, task) for task in tasks]
            
            for future in as_completed(futures):
                page_num, data_rows_page = future.result()
                if data_rows_page:
                    page_results[page_num] = data_rows_page
                    print(f"✓ 第{page_num}页: {len(data_rows_page)} 条")
        
        # 合并所有数据
        all_data = [row for page_num in sorted(page_results.keys()) for row in page_results[page_num]]
        
        # 创建DataFrame并保存
        df = pd.DataFrame(all_data, columns=table_headers).drop_duplicates()
        safe_title = re.sub(r'[\\/*?:<>|]', '_', title)
        filename = f"{safe_title}.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"✓ 成功! 已保存 {len(df)} 条记录\n{'-'*80}")
        return df
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None
