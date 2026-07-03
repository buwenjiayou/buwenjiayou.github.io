# 布文的个人学术主页

这是我的个人博客与学术展示网站仓库，用于集中整理个人介绍、科研兴趣、项目经历、学习记录与后续成果展示。网站当前以静态页面形式部署在 GitHub Pages 上，后续会逐步补充科研经历、代表项目、论文阅读笔记和阶段性总结。

## 网站入口

- 个人主页：[https://blog.buwen.homes/](https://blog.buwen.homes/)
- GitHub Pages 备用入口：[https://buwenjiayou.github.io/buwen.github.io/](https://buwenjiayou.github.io/buwen.github.io/)
- 仓库地址：[https://github.com/buwenjiayou/buwen.github.io](https://github.com/buwenjiayou/buwen.github.io)

## 网站定位

本网站面向个人长期学术与专业发展展示，重点包括：

- 个人简介与阶段性成长记录
- 科研兴趣、研究方向与学习脉络
- 项目实践、工程能力与作品展示
- 论文阅读、技术笔记与经验沉淀
- 后续申请、交流与个人品牌展示

当前博客尚未发布正式文章，主页已完成基础视觉设计、个人头像配置和 Markdown 发文流程。

## 仓库结构

```text
.
├── docs/
│   ├── index.html          # 网站主页
│   ├── tag.html            # 标签页
│   ├── rss.xml             # RSS 入口
│   ├── postList.json       # 文章索引
│   └── assets/
│       └── avatar.jpg      # 个人头像
├── posts/
│   └── _template.md        # Markdown 文章模板，不会被发布
├── scripts/
│   └── build_posts.py      # Markdown 文章生成脚本
├── .github/workflows/
│   └── pages.yml           # GitHub Pages 静态部署流程
├── config.json             # 站点基础配置
├── blogBase.json           # 站点元数据缓存
└── README.md
```

## 部署说明

网站通过 GitHub Actions 自动部署：

1. 修改 `main` 分支内容。
2. 如需发布文章，在 `posts/` 目录新增 Markdown 文件。
3. 推送到 GitHub。
4. `.github/workflows/pages.yml` 会先运行 `scripts/build_posts.py` 生成文章页面，再将 `docs/` 目录发布到 GitHub Pages。

自定义域名为：

```text
blog.buwen.homes
```

## 后续计划

- 完善个人简介、教育背景与研究兴趣
- 增加项目展示页面
- 整理论文阅读笔记与学习路线
- 补充科研训练、竞赛、实习或工程经历
- 根据申请与展示需求继续优化页面内容

## 维护说明

当前网站采用“自定义静态首页 + Markdown 文章生成”的方式维护。首页主体仍在 `docs/index.html` 中，文章内容放在 `posts/` 中。

### 发布新文章

复制 `posts/_template.md`，新建一个不以下划线开头的 Markdown 文件，例如：

```text
posts/research-note-001.md
```

文章开头需要保留 front matter：

```markdown
---
title: 文章标题
date: 2026-07-03
slug: research-note-001
tags: 科研, 学习
description: 一句话摘要。
---
```

字段说明：

- `title`：文章标题
- `date`：发布日期，格式为 `YYYY-MM-DD`
- `slug`：文章链接名，建议使用英文、数字和短横线
- `tags`：标签，多个标签用英文逗号分隔
- `description`：首页卡片和 RSS 中显示的摘要
- `pdf`：可选字段。若文章需要附带 PDF，把文件放到 `docs/assets/pdf/`，并填写相对文章页的路径，例如 `../assets/pdf/example.pdf`

写完文章后执行：

```bash
git add .
git commit -m "Add new post"
git push origin main
```

推送后 GitHub Actions 会自动生成：

- `docs/post/*.html`
- `docs/postList.json`
- `docs/tag.html`
- `docs/rss.xml`
- 首页最新文章区域

如果文章 front matter 中包含 `pdf:` 字段，文章页会自动显示“下载 PDF 原文”按钮。所有文章页默认带有点赞按钮；当前点赞数据保存在读者浏览器的 `localStorage` 中，适合纯静态站点的轻量交互，不依赖后端数据库。

### 本地预览生成

如果想在推送前本地生成一次文章页面：

```bash
python scripts/build_posts.py
```

然后打开 `docs/index.html` 查看效果。

后续如果重新启用 Gmeek 或其他博客生成器，需要注意避免自动生成流程覆盖当前自定义主页。
