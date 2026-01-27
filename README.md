# bluearXiv/不漏arXiv

自动获取arXiv上数学领域（AG, RT, QA）的最新论文，并生成LaTeX文档。

## 功能
- 每天自动获取math.AG, math.RT, math.QA三个领域的最新论文
- 生成格式化的LaTeX文档
- 自动统计论文数量
- 通过GitHub Actions定时运行

## 使用方法
1. 每天UTC时间6:00（北京时间14:00）自动运行
2. 生成的文件：`arxiv_YYYYMMDD.tex`
3. 最新的文件也会保存为`latest.tex`

## 其它
1. 主要用于私人用途，如需使用请自行部署和修改
2. 目前由于不清楚arXiv api的时间机制，以及arXiv本身由于假期/周末/其它原因的不更新，实际上抓取的是arXiv api认为最近的有论文发布的一天，但生成的tex文档的时间总是当天
3. arXiv文章本身存在时效性，数据可能出现奇怪的的行为
4. 感谢arXiv提供的api支持，请使用者遵循相关知识产权协议
