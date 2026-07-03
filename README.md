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

当前博客尚未发布正式文章，主页已完成基础视觉设计和个人头像配置。

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
├── .github/workflows/
│   └── pages.yml           # GitHub Pages 静态部署流程
├── config.json             # 站点基础配置
├── blogBase.json           # 站点元数据缓存
└── README.md
```

## 部署说明

网站通过 GitHub Actions 自动部署：

1. 修改 `main` 分支内容。
2. 推送到 GitHub。
3. `.github/workflows/pages.yml` 会自动将 `docs/` 目录发布到 GitHub Pages。

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

当前网站采用手写静态 HTML/CSS 维护，部署流程直接发布 `docs/` 目录。后续如果重新启用 Gmeek 或其他博客生成器，需要注意避免自动生成流程覆盖当前自定义主页。
