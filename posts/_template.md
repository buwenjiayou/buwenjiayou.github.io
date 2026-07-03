---
title: 文章标题
date: 2026-07-03
slug: my-first-post
tags: 科研, 学习
description: 这里写一句文章摘要，会显示在首页文章卡片和 RSS 中。
pdf: ../assets/pdf/example.pdf
---

# 文章标题

这里开始写正文。你可以使用常见 Markdown 语法：

## 二级标题

- 列表项
- **加粗**
- `行内代码`

```text
代码块
```

> 引用内容

图片可以放在 `docs/assets/` 里，然后这样引用：

```markdown
![图片说明](../assets/example.jpg)
```

如果文章需要附带 PDF，把 PDF 放在 `docs/assets/pdf/` 目录，并在上方 `pdf:` 字段填写从文章页出发的相对路径，例如：

```yaml
pdf: ../assets/pdf/example.pdf
```

文章页会自动显示“下载 PDF 原文”按钮，并自带本地点赞按钮。
