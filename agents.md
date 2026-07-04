# 本仓库协作与部署规则

## 默认交流

- 默认使用中文交流，包括状态更新、命令说明、提交说明和最终回复。
- 修改博客内容后，必须同时更新生成产物，不能只改 `posts/*.md`。

## 博客生成流程

- 文章源文件在 `posts/*.md`。
- 静态站点输出在 `docs/`。
- 每次修改文章、导航、标签页、RSS 页面或生成脚本后，都要运行：

```bash
python scripts/build_posts.py
```

- 生成后至少检查：
  - 相关 `docs/post/*.html` 是否包含最新内容。
  - `docs/index.html`、`docs/tag.html`、`docs/postList.json`、`docs/rss.xml` 是否按预期更新。
  - 若修改 RSS 说明页，还要检查 `docs/rss.html`。

## 提交与推送

- 提交前执行：

```bash
git status --short --branch
```

- 只暂存本次任务相关文件，避免把临时文件、缓存目录或无关未跟踪文件带入提交。
- 如果运行 Python 检查生成了 `__pycache__/`，提交前必须删除或确认未暂存。
- 推送后必须确认远端分支：

```bash
git ls-remote origin refs/heads/main
```

- 本地 `HEAD`、`origin/main` 和 `ls-remote` 返回的远端 hash 应一致，才说明 Git 推送本身成功。

## GitHub Pages 部署验证

本仓库使用 `.github/workflows/pages.yml` 发布 `docs/` 目录到 GitHub Pages。推送成功不等于网站已经发布成功。

每次推送后必须区分三层状态：

1. Git 仓库层：`git push` 是否成功，远端 `main` 是否更新。
2. GitHub 文件层：必要时检查 `raw.githubusercontent.com/.../main/docs/...` 是否已有最新文件。
3. Pages 发布层：访问 `https://blog.buwen.homes/...`，确认线上页面是否返回最新内容。

如果远端仓库已有最新文件，但网站仍旧旧内容或 404，优先判断为 Pages 部署延迟、CDN 缓存或 Pages workflow 失败，而不是重复改业务内容。

## Pages 失败处理经验

- 如果网站短时间没变，先等待 30 到 60 秒后带 cache-busting 参数复查，例如：

```text
https://blog.buwen.homes/rss.html?check=<commit>
```

- 如果 GitHub Actions 显示 `Deployment failed, try again later.`，通常是 GitHub Pages 发布服务临时失败，不是构建脚本失败。
- 这种情况下可以创建空提交触发重新部署：

```bash
git commit --allow-empty -m "Retry Pages deployment"
git push origin main
```

- 重试后再次访问线上页面，直到确认新内容可见。

## RSS 约定

- `docs/rss.xml` 保持标准 RSS 源文件，供阅读器订阅。
- 导航栏里的 RSS 链接指向 `docs/rss.html`，该页面面向普通访客解释如何订阅。
- 不要为了浏览器显示效果破坏 `rss.xml` 的标准 XML 格式。
