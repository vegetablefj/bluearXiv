#!/usr/bin/env python3
# test_arxiv_api.py
import arxiv
import datetime

print("🧪 arXiv API连接测试")
print("=" * 60)

# 测试arXiv API连接
try:
    client = arxiv.Client()
    
    # 测试一个肯定有论文的分类（比如cs.CV计算机视觉）
    test_category = "cs.CV"
    
    print(f"1. 测试arXiv API连接性...")
    print(f"   搜索分类: {test_category}")
    print(f"   当前时间: {datetime.datetime.now()}")
    
    # 搜索最近的论文
    search = arxiv.Search(
        query=f"cat:{test_category}",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = list(client.results(search))
    
    if papers:
        print(f"   ✅ 连接成功！找到 {len(papers)} 篇论文")
        print(f"\n2. 最近的论文信息:")
        for i, paper in enumerate(papers[:3], 1):
            days_ago = (datetime.datetime.now(datetime.timezone.utc) - paper.published).days
            print(f"   {i}. {paper.title[:70]}...")
            print(f"      日期: {paper.published.date()} ({days_ago}天前)")
            print(f"      ID: {paper.entry_id.split('/')[-1]}")
    else:
        print(f"   ⚠️  连接成功，但未找到论文")
        
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

print("\n" + "=" * 60)
print("3. 测试你的目标分类...")

# 测试你的目标分类
categories = ["math.AG", "math.RT", "math.QA"]
for category in categories:
    try:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=3,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        papers = list(client.results(search))
        
        if papers:
            latest_date = max(p.published.date() for p in papers)
            print(f"   {category}: 找到论文，最新的是 {latest_date}")
        else:
            print(f"   {category}: 没有找到任何论文")
            
    except Exception as e:
        print(f"   {category}: 错误 - {e}")

print("\n" + "=" * 60)
print("4. 诊断你的查询...")
print("   你的查询条件:")
print(f"   - 分类: math.AG, math.RT, math.QA")
print(f"   - 时间: 最近1天内 ({datetime.datetime.now().date()})")
print(f"   - 排序: 按提交日期降序")
print("\n   如果返回0篇论文，可能是因为:")
print("   a) 确实没有新论文（周末、节假日）")
print("   b) arXiv API暂时没有2026年的数据（因为是未来）")
print("   c) 网络或API限制")

print("\n" + "=" * 60)
print("5. 建议的解决方案:")
print("   A. 扩大时间范围:")
print('       修改 fetch_papers.py 中的 DAYS_BACK = 7')
print("   B. 获取更多结果:")
print('       修改 MAX_RESULTS = 100')
print("   C. 测试更多分类:")
print('       添加 cs.AI, cs.LG 等活跃领域')
print("\n   测试后，如果其他分类有数据，说明你的API连接正常！")