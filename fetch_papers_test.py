#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os
import time
import logging
from typing import List, Dict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
CATEGORIES = {
    "AG": "math.AG",
    "RT": "math.RT", 
    "QA": "math.QA"
}
MAX_RESULTS = 100
MAX_RETRIES = 3  # 添加重试机制
RETRY_DELAY = 5   # 重试延迟时间

# 修改 get_papers 函数中的查询构建部分
def get_papers(category: str) -> List[Dict]:
    """使用 arXiv API 直接获取论文"""
    # 计算日期范围
    today = datetime.now().date()
    yesterday = today - timedelta(days=3)
    
    # 格式化日期字符串为 YYYYMMDD
    start_date = yesterday.strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    # 构建查询 URL
    base_url = "https://export.arxiv.org/api/query"
    query = f"cat:{category}+AND+submittedDate:[{start_date}+TO+{end_date}]"
    
    # 完整的URL
    full_url = f"{base_url}?search_query={query}&max_results={MAX_RESULTS}&sortBy=submittedDate&sortOrder=descending"
    print(f"请求URL: {full_url}")  # 打印URL用于调试
    
    headers = {
        "User-Agent": "arXiv-Daily-Fetcher/1.0 (contact: vegetablefj@github)"
    }
    
    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析 XML 响应
        root = ET.fromstring(response.content)
        papers = []
        
        # 定义命名空间 - 这是关键！
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # 检查是否有条目
        entries = root.findall('atom:entry', ns)
        print(f"找到 {len(entries)} 个条目")
        
        for entry in entries:
            # 提取论文ID - 使用正确的命名空间
            id_elem = entry.find('atom:id', ns)
            paper_id = id_elem.text if id_elem is not None else None
            if paper_id:
                paper_id = paper_id.split('/')[-1]
            else:
                paper_id = "unknown"
            
            # 提取标题 - 使用正确的命名空间
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "无标题"
            
            # 提取作者 - 使用正确的命名空间
            authors = []
            author_elems = entry.findall('atom:author', ns)
            for author_elem in author_elems:
                name_elem = author_elem.find('atom:name', ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)
            
            # 提取发布时间 - 使用正确的命名空间
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text if published_elem is not None else None
            
            paper_info = {
                "id": paper_id,
                "title": title,
                "authors": authors,
                "published": published
            }
            papers.append(paper_info)
            # 打印第一篇论文的信息用于调试
            if len(papers) == 1:
                print("第一篇论文信息:", paper_info)
        
        return papers
        
    except Exception as e:
        print(f"请求失败: {e}")
        return []

def format_authors(authors: List[str]) -> str:
    """格式化作者列表"""
    if len(authors) > 3:
        return ", ".join(authors[:3]) + " 等"
    return ", ".join(authors)

def main():
    print("🔍 开始获取arXiv论文（直接API版本）...")
    start_time = time.time()
    
    # 获取当天日期（用于显示）
    today = datetime.now().date()
    today_str = f"{today.year}年{today.month}月{today.day}日"
    
    # 分别获取各分类论文
    papers_ag = get_papers("math.AG")
    time.sleep(1)  # 避免请求过快
    
    papers_rt = get_papers("math.RT")
    time.sleep(1)
    
    papers_qa = get_papers("math.QA")
    
    # 合并RT和QA
    papers_rt_qa = papers_rt + papers_qa
    
    # 统计数量
    ag_count = len(papers_ag)
    rt_count = len(papers_rt)
    qa_count = len(papers_qa)
    rt_qa_count = len(papers_rt_qa)
    
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 统计结果 (耗时: {elapsed_time:.1f}秒):")
    print(f"  报告生成日期: {today_str}")
    print(f"  AG: {ag_count} 篇")
    print(f"  RT: {rt_count} 篇")
    print(f"  QA: {qa_count} 篇")
    print(f"  RT+QA 总计: {rt_qa_count} 篇")
    
    # 检查模板文件
    try:
        with open('template.tex', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ 错误: 未找到 template.tex 文件")
        return
    
    # 替换数量命令
    template = template.replace(
        r"\newcommand{\AGnumber}{1}", 
        f"\\newcommand{{\\AGnumber}}{{{ag_count}}}"
    )
    template = template.replace(
        r"\newcommand{\RTQAnumber}{2}", 
        f"\\newcommand{{\\RTQAnumber}}{{{rt_qa_count}}}"
    )
    
    # 替换日期命令
    template = template.replace(
        r"\newcommand{\NewestDate}{}", 
        f"\\newcommand{{\\NewestDate}}{{{today_str}}}"
    )
    
    # 生成AG部分的论文条目
    ag_entries = []
    for paper in papers_ag:
        authors = format_authors(paper['authors'])
        ag_entries.append(f"\\arxiv{{{paper['id']}}}{{{paper['title']}}}{{{authors}}}\n\n")
    
    # 生成RT&QA部分的论文条目
    rt_qa_entries = []
    for paper in papers_rt_qa:
        authors = format_authors(paper['authors'])
        rt_qa_entries.append(f"\\arxiv{{{paper['id']}}}{{{paper['title']}}}{{{authors}}}\n\n")
    
    # 替换模板中的占位符
    if "%AG begin\n\n%AG end" in template:
        ag_content = "%AG begin\n" + "".join(ag_entries) + "%AG end"
        template = template.replace("%AG begin\n\n%AG end", ag_content)
    
    if "%RT&QA begin\n\n%RT&QA end" in template:
        rt_qa_content = "%RT&QA begin\n" + "".join(rt_qa_entries) + "%RT&QA end"
        template = template.replace("%RT&QA begin\n\n%RT&QA end", rt_qa_content)
    
    # 确保输出目录存在
    output_dir = "Daily Tex Documents"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存文件
    today_file_str = datetime.now().strftime("%Y%m%d")
    output_filename = os.path.join(output_dir, f"arxiv_{today_file_str}.tex")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    # latest.tex 仍然保存在根目录
    with open("latest.tex", 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"\n✅ 已生成文件:")
    print(f"   {output_filename}")
    print(f"   latest.tex (最新版，根目录)")

if __name__ == "__main__":
    main()