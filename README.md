# bluearXiv

自动获取arXiv上数学领域（AG, RT, QA）的最新论文，并生成LaTeX文档。

## 功能
- 每天自动获取math.AG, math.RT, math.QA三个领域的最新论文
- 生成格式化的LaTeX文档
- 自动统计论文数量
- 通过GitHub Actions定时运行

## 使用方法
1. 每天UTC时间1:00（北京时间9:00）自动运行
2. 生成的文件：`arxiv_YYYYMMDD.tex`
3. 最新的文件也会保存为`latest.tex`

## 本地运行