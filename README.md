# 批量页面生成器

将你导入的 CSV 或 JSON 页面数据渲染为独立 Markdown 页面。每条记录必须提供真实、可核验且与主题相关的内容；工具不使用隐藏链接、关键词堆砌或其他规避搜索引擎规则的机制。

## GitHub 自动生成

CSV 生产数据文件是 `data/pages.csv`。三级模板页面由 `data/site.json`、`data/batches/*.json`、单页 JSON 和 `data/render-jobs.json` 组合。将它们提交到 GitHub 的 `main` 分支后，`.github/workflows/generate-pages.yml` 会自动运行 Python、生成 `generated/` 中的 Markdown 页面并把变化提交回仓库。

首次使用前，在仓库的 **Settings → Actions → General → Workflow permissions** 选择 **Read and write permissions**，以允许工作流提交生成结果。

## 快速开始

```powershell
py generate.py --input data/pages.sample.csv --output generated
```

输出页面位于 `generated/YYYY/MM/slug.md`，同时会生成 `generated/manifest.json`。

## CSV 字段

必填：`title`、`keyword`、`summary`、`body`。

可选字段：

| 字段 | 作用 |
|---|---|
| `style` | `guide`、`overview` 或 `update`，决定页面布局。 |
| `source_id` | 数据源中的永久唯一 ID；用于识别同一条内容的更新，强烈建议提供。 |
| `slug` | URL/文件名；省略时根据标题生成。 |
| `published_at`、`updated_at` | ISO 8601 时间；省略时使用当前 UTC 时间。 |
| `image` | 图片 HTTPS URL。 |
| `source_url` | 原始或官方资料 HTTPS URL。 |
| `cta_label`、`cta_url` | 页面底部行动链接。 |
| `markers` | 逗号分隔的标签或要点。 |
| `news_json` | JSON 数组，如 `[{"title":"资讯标题","url":"https://...","summary":"摘要"}]`。 |
| `related_json` | JSON 数组，格式同 `news_json`，用于站内相关推荐。 |

JSON 导入时，文件顶层是页面对象数组，字段名相同；`news_json` 与 `related_json` 可以直接填写数组。

## 导入你的数据

复制 `data/pages.sample.csv` 为新的 CSV，替换其中数据后执行：

```powershell
py generate.py --input data/your-pages.csv --output generated
```

示例 CSV 已使用 UTF-8 BOM 编码，可直接用 Excel 打开。用 Excel 保存自己的文件时，请选择“CSV UTF-8（逗号分隔）”，否则中文可能显示乱码。

生成器会拒绝：缺失必填字段、重复 slug、非 HTTP(S) 链接、错误的 JSON 数组字段。

## 防重复策略

每次运行都会读取 `generated/manifest.json`：

- 相同 `source_id` 且内容未变：跳过；
- 相同 `source_id` 但内容变化：原路径更新，不新建第二页；
- 不同 `source_id` 但内容指纹或标题相同：跳过重复页；
- 同一份导入数据内重复的 `source_id`、标题或内容：只保留首条。

内容指纹基于关键词、摘要、正文、图片、来源、CTA、标签、相关新闻和相关推荐计算。它检测的是完全相同的内容；相近但不同的文章仍需由导入数据和人工审核保证质量。

此外，所有新页面必须与内容库中已有页面至少有 **50% 内容差异**。差异计算只使用页面标题、关键词、摘要、正文、标签、相关资讯和相关推荐，不会因为模板中的固定标题或页脚而误判。差异不足 50% 的新页面会被跳过；同一 `source_id` 的已有页面仍会原位更新。

默认阈值是 `0.50`，可提高要求，例如至少 70% 不同：

```powershell
py generate.py --input data/your-pages.csv --output generated --min-difference 0.70
```
