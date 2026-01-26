#!/usr/bin/env python3
import arxiv
import datetime
import time
import random
from typing import List, Dict
import logging
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
CATEGORIES = {
    "AG": "math.AG",
    "RT": "math.RT", 
    "QA": "math.QA"
}
MAX_RESULTS = 50
MAX_RETRIES = 3
RETRY_DELAY = 5

def get_papers_with_retry(category: str, max_results: int) -> List[Dict]:
    """带重试机制的论文获取函数"""
    client = arxiv.Client()
    
    for attempt in range(MAX_RETRIES):
        try:
            # 构建搜索
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            logger.info(f"尝试获取 {category} 的论文 (第{attempt+1}次尝试)...")
            
            for result in client.results(search):
                paper = {
                    "id": result.entry_id.split('/')[-1],
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "published": result.published,
                    "published_date": result.published.date()
                }
                papers.append(paper)
            
            logger.info(f"成功获取 {len(papers)} 篇 {category} 论文")
            return papers
            
        except Exception as e:
            logger.warning(f"第{attempt+1}次尝试获取 {category} 失败: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error(f"获取 {category} 失败，已达最大重试次数")
                return []
    
    return []

def get_papers(category: str) -> List[Dict]:
    """获取指定分类的最新论文"""
    return get_papers_with_retry(category, MAX_RESULTS)

def format_authors(authors: List[str]) -> str:
    """格式化作者列表"""
    if len(authors) > 3:
        return ", ".join(authors[:3]) + " 等"
    return ", ".join(authors)

def find_latest_paper_date(papers_list: List[List[Dict]]) -> datetime.date:
    """找到所有论文中最新的日期"""
    all_dates = set()
    
    for papers in papers_list:
        for paper in papers:
            all_dates.add(paper['published_date'])
    
    if all_dates:
        return max(all_dates)
    else:
        return datetime.datetime.now().date()

def filter_papers_by_date(papers: List[Dict], target_date: datetime.date) -> List[Dict]:
    """过滤出指定日期的论文"""
    return [p for p in papers if p['published_date'] == target_date]

def main():
    print("🔍 开始获取arXiv论文...")
    start_time = time.time()
    
    # 获取当天日期（用于显示）
    today = datetime.datetime.now().date()
    today_str = f"{today.year}年{today.month}月{today.day}日"
    
    # 分别获取各分类论文
    papers_ag = get_papers(CATEGORIES["AG"])
    papers_rt = get_papers(CATEGORIES["RT"])
    papers_qa = get_papers(CATEGORIES["QA"])
    
    # 找到最新有论文的日期
    latest_date = find_latest_paper_date([papers_ag, papers_rt, papers_qa])
    latest_date_str = f"{latest_date.year}年{latest_date.month}月{latest_date.day}日"
    
    print(f"📅 日期信息:")
    print(f"  报告生成日期: {today_str}")
    print(f"  最新论文日期: {latest_date_str}")
    
    # 过滤出最新日期的论文
    ag_latest = filter_papers_by_date(papers_ag, latest_date)
    rt_latest = filter_papers_by_date(papers_rt, latest_date)
    qa_latest = filter_papers_by_date(papers_qa, latest_date)
    
    # 合并RT和QA，按时间排序
    rt_qa_latest = rt_latest + qa_latest
    rt_qa_latest.sort(key=lambda x: x['published'], reverse=True)
    
    elapsed_time = time.time() - start_time
    print(f"\n📊 论文统计 (耗时: {elapsed_time:.1f}秒):")
    print(f"  AG: 获取{len(papers_ag)}篇 → {latest_date_str}有{len(ag_latest)}篇")
    print(f"  RT: 获取{len(papers_rt)}篇 → {latest_date_str}有{len(rt_latest)}篇") 
    print(f"  QA: 获取{len(papers_qa)}篇 → {latest_date_str}有{len(qa_latest)}篇")
    print(f"  RT+QA 总计: {len(rt_qa_latest)} 篇")
    
    # 检查模板文件
    try:
        with open('template.tex', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ 错误: 未找到 template.tex 文件")
        return
    
    # 替换数量命令 - 使用最新日期的论文数量
    template = template.replace(
        r"\newcommand{\AGnumber}{1}", 
        f"\\newcommand{{\\AGnumber}}{{{len(ag_latest)}}}"
    )
    template = template.replace(
        r"\newcommand{\RTQAnumber}{2}", 
        f"\\newcommand{{\\RTQAnumber}}{{{len(rt_qa_latest)}}}"
    )
    
    # 替换日期命令 - 使用当天日期
    template = template.replace(
        r"\newcommand{\NewestDate}{}", 
        f"\\newcommand{{\\NewestDate}}{{{today_str}}}"
    )
    
    # 生成AG部分的论文条目
    ag_entries = []
    for paper in ag_latest:
        authors = format_authors(paper['authors'])
        ag_entries.append(f"\\arxiv{{{paper['id']}}}{{{paper['title']}}}{{{authors}}}\n\n")
    
    # 生成RT&QA部分的论文条目
    rt_qa_entries = []
    for paper in rt_qa_latest:
        authors = format_authors(paper['authors'])
        rt_qa_entries.append(f"\\arxiv{{{paper['id']}}}{{{paper['title']}}}{{{authors}}}\n\n")
    
    # 替换模板中的占位符
    if "%AG begin\n\n%AG end" in template:
        ag_content = "%AG begin\n" + "".join(ag_entries) + "%AG end"
        template = template.replace("%AG begin\n\n%AG end", ag_content)
    else:
        print("⚠️  警告: 未找到 AG 占位符")
    
    if "%RT&QA begin\n\n%RT&QA end" in template:
        rt_qa_content = "%RT&QA begin\n" + "".join(rt_qa_entries) + "%RT&QA end"
        template = template.replace("%RT&QA begin\n\n%RT&QA end", rt_qa_content)
    else:
        print("⚠️  警告: 未找到 RT&QA 占位符")
    
    # 添加注释信息
    comment = f"% 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    comment += f"% 报告日期: {today_str}\n"
    comment += f"% 论文日期: {latest_date_str}\n"
    comment += f"% AG论文: {len(ag_latest)}篇\n"
    comment += f"% RT&QA论文: {len(rt_qa_latest)}篇\n\n"
    
    template = comment + template
    
    # 保存文件
    output_filename = f"arxiv_{today.strftime('%Y%m%d')}.tex"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    # 也保存一个latest.tex方便查看
    with open("latest.tex", 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"\n✅ 已生成文件:")
    print(f"   {output_filename}")
    print(f"   latest.tex (最新版)")
    print(f"   报告日期: {today_str}")
    print(f"   显示的论文日期: {latest_date_str}")
    
    # 显示详细统计
    print(f"\n📋 详细统计:")
    print(f"  AG: {len(ag_latest)}篇 ({latest_date_str}的论文)")
    print(f"  RT: {len(rt_latest)}篇 ({latest_date_str}的论文)")
    print(f"  QA: {len(qa_latest)}篇 ({latest_date_str}的论文)")
    print(f"  RT+QA: {len(rt_qa_latest)}篇")
    
    if len(ag_latest) + len(rt_qa_latest) == 0:
        print("\n⚠️  注意: 没有找到任何论文，可能是因为:")
        print("  1. arXiv API暂时没有数据")
        print("  2. 网络连接问题")
        print("  3. 指定的分类在所选日期没有新论文")

if __name__ == "__main__":
    main()