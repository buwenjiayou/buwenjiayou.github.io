from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
DOCS_DIR = ROOT / "docs"
POST_DIR = DOCS_DIR / "post"
SITE_TITLE = "布文的博客"
SITE_URL = "https://blog.buwen.homes"
SITE_DESCRIPTION = "记录学习、研究、项目与生活。"


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def parse_tags(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    tags = [item.strip().strip('"').strip("'") for item in raw.split(",")]
    return [tag for tag in tags if tag]


def slugify(value: str, fallback: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9_-]+", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            class_name = f' class="language-{html.escape(language)}"' if language else ""
            blocks.append(f"<pre><code{class_name}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append(f"<li>{inline_markdown(item)}</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(f"<li>{inline_markdown(item)}</li>")
                i += 1
            blocks.append("<ol>" + "".join(items) + "</ol>")
            continue

        if stripped.startswith(">"):
            quotes: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quotes.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(f"<blockquote>{inline_markdown(' '.join(quotes))}</blockquote>")
            continue

        paragraph = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4})\s+|^[-*]\s+|^\d+\.\s+|^>|^```", lines[i].strip()):
            paragraph.append(lines[i].strip())
            i += 1
        blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")

    return "\n".join(blocks)


def read_posts() -> list[dict[str, object]]:
    posts: list[dict[str, object]] = []
    POSTS_DIR.mkdir(exist_ok=True)
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title") or path.stem
        date = meta.get("date") or dt.date.today().isoformat()
        description = meta.get("description") or ""
        pdf = meta.get("pdf") or ""
        tags = parse_tags(meta.get("tags", ""))
        slug = slugify(meta.get("slug") or path.stem, f"post-{len(posts) + 1}")
        posts.append(
            {
                "source": path,
                "title": title,
                "date": date,
                "description": description,
                "tags": tags,
                "slug": slug,
                "url": f"post/{slug}.html",
                "pdf": pdf,
                "html": markdown_to_html(body),
            }
        )
    posts.sort(key=lambda item: str(item["date"]), reverse=True)
    return posts


def page_shell(title: str, body: str, description: str = SITE_DESCRIPTION) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{html.escape(description)}">
    <link rel="icon" href="../assets/avatar.jpg">
    <title>{html.escape(title)} - {SITE_TITLE}</title>
    <script>
        const savedTheme = localStorage.getItem("site-theme") || "light";
        document.documentElement.dataset.theme = savedTheme;
    </script>
    <style>
        :root {{
            color-scheme: light;
            --text: #19222d;
            --muted: #5f6b7a;
            --soft: rgba(255, 255, 255, 0.78);
            --softer: rgba(255, 255, 255, 0.46);
            --border: rgba(255, 255, 255, 0.56);
            --shadow: 0 24px 70px rgba(42, 55, 82, 0.20);
        }}
        html[data-theme="dark"] {{
            color-scheme: dark;
            --text: #eef4ff;
            --muted: #b9c4d6;
            --soft: rgba(18, 24, 38, 0.72);
            --softer: rgba(18, 24, 38, 0.42);
            --border: rgba(255, 255, 255, 0.16);
            --shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            min-width: 280px;
            min-height: 100vh;
            margin: 0;
            color: var(--text);
            font-family: Inter, "SF Pro Display", "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.75;
            background:
                linear-gradient(120deg, rgba(238, 246, 255, 0.62), rgba(255, 248, 241, 0.40)),
                url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center / cover fixed;
        }}
        html[data-theme="dark"] body {{
            background:
                linear-gradient(120deg, rgba(5, 10, 22, 0.72), rgba(23, 29, 48, 0.58)),
                url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center / cover fixed;
        }}
        a {{ color: inherit; }}
        .site-shell {{
            width: min(920px, calc(100% - 36px));
            min-height: 100vh;
            margin: 0 auto;
            padding: 24px 0 34px;
        }}
        .topbar, .article {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--soft);
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }}
        .topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            min-height: 64px;
            padding: 12px 16px 12px 18px;
        }}
        .brand {{ display: flex; align-items: center; gap: 12px; color: var(--text); text-decoration: none; font-weight: 800; }}
        .nav {{ display: flex; align-items: center; justify-content: flex-end; gap: 6px; flex-wrap: wrap; }}
        .nav a, .theme-toggle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 38px;
            padding: 0 12px;
            border: 1px solid transparent;
            border-radius: 8px;
            color: var(--muted);
            background: transparent;
            font: inherit;
            text-decoration: none;
            cursor: pointer;
        }}
        .nav a:hover, .theme-toggle:hover {{ color: var(--text); border-color: var(--border); background: var(--softer); }}
        .article {{ margin-top: 36px; padding: clamp(24px, 5vw, 56px); }}
        .article h1 {{ margin: 0; font-size: clamp(34px, 6vw, 62px); line-height: 1.08; }}
        .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 34px; color: var(--muted); font-size: 14px; }}
        .tag {{ display: inline-flex; min-height: 24px; align-items: center; padding: 0 8px; border: 1px solid var(--border); border-radius: 999px; background: var(--softer); }}
        .article-actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin: -14px 0 28px; }}
        .download-button, .like-button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 32px;
            padding: 0 10px;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            background: var(--softer);
            font: inherit;
            font-size: 13px;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
            transition: transform .16s ease, background .16s ease, color .16s ease, border-color .16s ease;
        }}
        .like-button:hover {{ transform: translateY(-1px); }}
        .download-button {{ color: #fff; border-color: transparent; background: linear-gradient(135deg, #5271ff, #48c6ef); }}
        .like-button.is-liked {{ color: #fff; border-color: transparent; background: linear-gradient(135deg, #ff6b8b, #ff9a62); }}
        .like-button.is-pulsing {{ animation: likePulse .34s ease; }}
        @keyframes likePulse {{
            0% {{ transform: scale(1); }}
            45% {{ transform: scale(1.06); }}
            100% {{ transform: scale(1); }}
        }}
        .content {{ font-size: 17px; }}
        .content h2 {{ margin-top: 34px; }}
        .content h3 {{ margin-top: 28px; }}
        .content p {{ margin: 16px 0 0; }}
        .content img {{ max-width: 100%; border-radius: 8px; }}
        .content pre {{ overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; padding: 16px; border-radius: 8px; background: rgba(15, 23, 42, 0.88); color: #f8fafc; }}
        .content code {{ font-family: "SFMono-Regular", Consolas, monospace; }}
        .content blockquote {{
            margin: 14px 0;
            padding: 14px 16px;
            border: 1px solid var(--border);
            border-left: 4px solid #5271ff;
            border-radius: 8px;
            background: var(--softer);
            color: var(--text);
            font-size: 16px;
            line-height: 1.75;
            overflow-wrap: anywhere;
            white-space: normal;
        }}
        footer {{ margin-top: 24px; color: rgba(255,255,255,.88); text-shadow: 0 1px 12px rgba(0,0,0,.24); font-size: 14px; }}
        @media (max-width: 640px) {{
            .site-shell {{ width: calc(100% - 18px); padding-top: 14px; }}
            .topbar {{ align-items: flex-start; flex-direction: column; }}
            .nav {{ justify-content: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="site-shell">
        <header class="topbar">
            <a class="brand" href="../">
                <span>{SITE_TITLE}</span>
            </a>
            <nav class="nav">
                <a href="../">主页</a>
                <a href="../tag.html">标签</a>
                <a href="../rss.html">RSS</a>
                <button class="theme-toggle" type="button" aria-label="切换明暗主题" onclick="toggleTheme()">☀</button>
            </nav>
        </header>
        {body}
        <footer>Copyright © <span id="copyrightYear"></span> {SITE_TITLE}</footer>
    </div>
    <script>
        const toggle = document.querySelector(".theme-toggle");
        function syncThemeIcon() {{
            toggle.textContent = document.documentElement.dataset.theme === "dark" ? "☾" : "☀";
        }}
        function toggleTheme() {{
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = nextTheme;
            localStorage.setItem("site-theme", nextTheme);
            syncThemeIcon();
        }}
        function setupLikeButton() {{
            const button = document.querySelector("[data-like-slug]");
            if (!button) return;
            const slug = button.dataset.likeSlug;
            const key = `blog-like-${{slug}}`;
            const liked = localStorage.getItem(key) === "1";
            function render(active) {{
                button.classList.toggle("is-liked", active);
                button.setAttribute("aria-pressed", active ? "true" : "false");
                button.textContent = active ? "已点亮" : "点亮这篇";
                button.title = active ? "已保存在当前浏览器" : "只保存在当前浏览器";
            }}
            render(liked);
            button.addEventListener("click", () => {{
                const currentLiked = localStorage.getItem(key) === "1";
                const nextLiked = !currentLiked;
                if (nextLiked) {{
                    localStorage.setItem(key, "1");
                }} else {{
                    localStorage.removeItem(key);
                }}
                render(nextLiked);
                button.classList.remove("is-pulsing");
                void button.offsetWidth;
                button.classList.add("is-pulsing");
            }});
        }}
        document.getElementById("copyrightYear").textContent = new Date().getFullYear();
        syncThemeIcon();
        setupLikeButton();
    </script>
</body>
</html>
"""


def render_post(post: dict[str, object]) -> str:
    tags = "".join(f'<span class="tag">{html.escape(str(tag))}</span>' for tag in post["tags"])
    actions = [f'<button class="like-button" type="button" data-like-slug="{html.escape(str(post["slug"]))}" aria-pressed="false" title="只保存在当前浏览器">点亮这篇</button>']
    if post.get("pdf"):
        actions.insert(
            0,
            f'<a class="download-button" href="{html.escape(str(post["pdf"]))}" download>下载 PDF 原文</a>',
        )
    action_html = "\n                ".join(actions)
    body = f"""<article class="article">
            <h1>{html.escape(str(post["title"]))}</h1>
            <div class="meta">
                <span>{html.escape(str(post["date"]))}</span>
                {tags}
            </div>
            <div class="article-actions">
                {action_html}
            </div>
            <div class="content">
{post["html"]}
            </div>
        </article>"""
    return page_shell(str(post["title"]), body, str(post["description"] or SITE_DESCRIPTION))


def render_index_posts(posts: list[dict[str, object]]) -> str:
    if not posts:
        return """<!-- POSTS_START -->
            <section class="empty-posts" aria-label="文章列表">
                <div>
                    <h2>暂未发布文章</h2>
                    <p>等你准备好内容后，在仓库的 posts 目录新增 Markdown 文件并推送，首页会自动展示最新文章。</p>
                </div>
                <div class="empty-icon" aria-hidden="true">+</div>
            </section>
            <!-- POSTS_END -->"""
    cards = []
    for post in posts[:6]:
        tags = "".join(f'<span class="tag-pill">{html.escape(str(tag))}</span>' for tag in post["tags"])
        description = html.escape(str(post["description"] or "点击阅读这篇文章。"))
        cards.append(
            f"""                <a class="post-card" href="{html.escape(str(post["url"]))}" data-like-card="{html.escape(str(post["slug"]))}">
                    <div class="post-meta">
                        <span>{html.escape(str(post["date"]))}</span>
                        {tags}
                    </div>
                    <h3>{html.escape(str(post["title"]))}</h3>
                    <p>{description}</p>
                </a>"""
        )
    return f"""<!-- POSTS_START -->
            <section class="posts-panel" aria-label="文章列表">
                <div class="posts-head">
                    <h2>最新文章</h2>
                    <span>共 {len(posts)} 篇</span>
                </div>
{chr(10).join(cards)}
            </section>
            <!-- POSTS_END -->"""


def update_index(posts: list[dict[str, object]]) -> None:
    path = DOCS_DIR / "index.html"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"<!-- POSTS_START -->.*?<!-- POSTS_END -->", re.S)
    text = pattern.sub(render_index_posts(posts), text)
    tag_count = len({tag for post in posts for tag in post["tags"]})
    text = re.sub(r"<strong>\d+</strong>\s*\n\s*<span>文章</span>", f"<strong>{len(posts)}</strong>\n                                <span>文章</span>", text, count=1)
    text = re.sub(r"<strong>\d+</strong>\s*\n\s*<span>标签</span>", f"<strong>{tag_count}</strong>\n                                <span>标签</span>", text, count=1)
    path.write_text(text, encoding="utf-8", newline="\n")


def render_tag_page(posts: list[dict[str, object]]) -> str:
    labels: dict[str, list[dict[str, object]]] = {}
    for post in posts:
        for tag in post["tags"]:
            labels.setdefault(str(tag), []).append(post)
    if not labels:
        content = """<h1>标签</h1>
            <p>暂时还没有发布文章，所以这里还没有标签。等后续内容上线后，标签会用于整理学习笔记、项目记录和研究方向。</p>
            <span class="empty">当前 0 个标签</span>"""
    else:
        groups = []
        for tag in sorted(labels):
            links = "".join(
                f'<li><a href="{html.escape(str(post["url"]))}">{html.escape(str(post["title"]))}</a><span>{html.escape(str(post["date"]))}</span></li>'
                for post in labels[tag]
            )
            groups.append(f"""<section class="tag-group">
                <h2>#{html.escape(tag)}</h2>
                <ul>{links}</ul>
            </section>""")
        content = f"""<h1>标签</h1>
            <p>当前共 {len(labels)} 个标签，{len(posts)} 篇文章。</p>
            {''.join(groups)}"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{SITE_TITLE}标签页">
    <link rel="icon" href="assets/avatar.jpg">
    <title>标签 - {SITE_TITLE}</title>
    <script>
        const savedTheme = localStorage.getItem("site-theme") || "light";
        document.documentElement.dataset.theme = savedTheme;
    </script>
    <style>
        :root {{ color-scheme: light; --text:#19222d; --muted:#5f6b7a; --soft:rgba(255,255,255,.74); --softer:rgba(255,255,255,.46); --border:rgba(255,255,255,.56); --shadow:0 24px 70px rgba(42,55,82,.20); }}
        html[data-theme="dark"] {{ color-scheme: dark; --text:#eef4ff; --muted:#b9c4d6; --soft:rgba(18,24,38,.68); --softer:rgba(18,24,38,.42); --border:rgba(255,255,255,.16); --shadow:0 24px 70px rgba(0,0,0,.34); }}
        * {{ box-sizing:border-box; }}
        body {{ min-width:280px; min-height:100vh; margin:0; color:var(--text); font-family:Inter,"SF Pro Display","Segoe UI","Microsoft YaHei",Arial,sans-serif; line-height:1.65; background:linear-gradient(120deg,rgba(238,246,255,.62),rgba(255,248,241,.40)),url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center/cover fixed; }}
        html[data-theme="dark"] body {{ background:linear-gradient(120deg,rgba(5,10,22,.72),rgba(23,29,48,.58)),url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center/cover fixed; }}
        a {{ color:inherit; text-decoration:none; }}
        .site-shell {{ width:min(980px,calc(100% - 36px)); min-height:100vh; margin:0 auto; padding:24px 0 34px; }}
        .topbar,.panel {{ border:1px solid var(--border); border-radius:8px; background:var(--soft); box-shadow:var(--shadow); backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px); }}
        .topbar {{ display:flex; align-items:center; justify-content:space-between; gap:18px; min-height:64px; padding:12px 16px 12px 18px; }}
        .brand {{ display:flex; align-items:center; gap:12px; min-width:0; font-weight:800; }}
        .nav {{ display:flex; align-items:center; justify-content:flex-end; gap:6px; flex-wrap:wrap; }}
        .nav a,.theme-toggle {{ display:inline-flex; align-items:center; justify-content:center; min-height:38px; padding:0 12px; border:1px solid transparent; border-radius:8px; color:var(--muted); background:transparent; font:inherit; cursor:pointer; }}
        .nav a:hover,.theme-toggle:hover {{ color:var(--text); border-color:var(--border); background:var(--softer); }}
        .panel {{ margin-top:36px; padding:clamp(28px,6vw,58px); }}
        h1 {{ margin:0; font-size:clamp(38px,7vw,72px); line-height:1; }}
        p {{ max-width:640px; margin:18px 0 0; color:var(--muted); font-size:18px; }}
        .empty {{ display:inline-flex; align-items:center; min-height:42px; margin-top:28px; padding:0 14px; border:1px solid var(--border); border-radius:8px; background:var(--softer); color:var(--muted); font-weight:700; }}
        .tag-group {{ margin-top:30px; }}
        .tag-group h2 {{ margin:0 0 12px; }}
        .tag-group ul {{ display:grid; gap:10px; padding:0; list-style:none; }}
        .tag-group li {{ display:flex; justify-content:space-between; gap:16px; padding:14px 16px; border:1px solid var(--border); border-radius:8px; background:var(--softer); }}
        .tag-group span {{ color:var(--muted); font-size:14px; }}
        footer {{ margin-top:24px; color:rgba(255,255,255,.88); text-shadow:0 1px 12px rgba(0,0,0,.24); font-size:14px; }}
        @media (max-width:640px) {{ .site-shell {{ width:calc(100% - 18px); padding-top:14px; }} .topbar {{ align-items:flex-start; flex-direction:column; }} .nav {{ justify-content:flex-start; }} .tag-group li {{ flex-direction:column; }} }}
    </style>
</head>
<body>
    <div class="site-shell">
        <header class="topbar">
            <a class="brand" href="./"><span>{SITE_TITLE}</span></a>
            <nav class="nav"><a href="./">主页</a><a href="rss.html">RSS</a><a href="https://github.com/buwenjiayou" target="_blank" rel="noreferrer">GitHub</a><button class="theme-toggle" type="button" aria-label="切换明暗主题" onclick="toggleTheme()">☀</button></nav>
        </header>
        <main class="panel">
            {content}
        </main>
        <footer>Copyright © <span id="copyrightYear"></span> {SITE_TITLE}</footer>
    </div>
    <script>
        const toggle = document.querySelector(".theme-toggle");
        function syncThemeIcon() {{ toggle.textContent = document.documentElement.dataset.theme === "dark" ? "☾" : "☀"; }}
        function toggleTheme() {{ const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = nextTheme; localStorage.setItem("site-theme", nextTheme); syncThemeIcon(); }}
        document.getElementById("copyrightYear").textContent = new Date().getFullYear();
        syncThemeIcon();
    </script>
</body>
</html>
"""


def write_post_list(posts: list[dict[str, object]]) -> None:
    label_colors = {
        "科研": "#0969da",
        "学习": "#1f883d",
        "项目": "#8250df",
        "生活": "#bc4c00",
    }
    data: dict[str, object] = {}
    for index, post in enumerate(posts, start=1):
        data[f"P{index}"] = {
            "labels": post["tags"],
            "postTitle": post["title"],
            "postUrl": post["url"],
            "createdDate": post["date"],
            "dateLabelColor": "#1f883d",
        }
        for tag in post["tags"]:
            label_colors.setdefault(str(tag), "#5271ff")
    data["labelColorDict"] = label_colors if posts else {}
    (DOCS_DIR / "postList.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8", newline="\n")


def render_rss_page() -> str:
    feed_url = f"{SITE_URL}/rss.xml"
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{SITE_TITLE} RSS 订阅说明">
    <link rel="icon" href="assets/avatar.jpg">
    <link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="rss.xml">
    <title>RSS 订阅 - {SITE_TITLE}</title>
    <script>
        const savedTheme = localStorage.getItem("site-theme") || "light";
        document.documentElement.dataset.theme = savedTheme;
    </script>
    <style>
        :root {{
            color-scheme: light;
            --text: #19222d;
            --muted: #5f6b7a;
            --soft: rgba(255, 255, 255, 0.76);
            --softer: rgba(255, 255, 255, 0.48);
            --border: rgba(255, 255, 255, 0.56);
            --accent: #5271ff;
            --shadow: 0 24px 70px rgba(42, 55, 82, 0.20);
        }}
        html[data-theme="dark"] {{
            color-scheme: dark;
            --text: #eef4ff;
            --muted: #b9c4d6;
            --soft: rgba(18, 24, 38, 0.70);
            --softer: rgba(18, 24, 38, 0.44);
            --border: rgba(255, 255, 255, 0.16);
            --accent: #7aa2ff;
            --shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            min-width: 280px;
            min-height: 100vh;
            margin: 0;
            color: var(--text);
            font-family: Inter, "SF Pro Display", "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.7;
            background:
                linear-gradient(120deg, rgba(238, 246, 255, 0.62), rgba(255, 248, 241, 0.40)),
                url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center / cover fixed;
        }}
        html[data-theme="dark"] body {{
            background:
                linear-gradient(120deg, rgba(5, 10, 22, 0.72), rgba(23, 29, 48, 0.58)),
                url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=2200&q=85") center / cover fixed;
        }}
        a {{ color: inherit; text-decoration: none; }}
        .site-shell {{
            width: min(980px, calc(100% - 36px));
            min-height: 100vh;
            margin: 0 auto;
            padding: 24px 0 34px;
        }}
        .topbar, .panel {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--soft);
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }}
        .topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            min-height: 64px;
            padding: 12px 16px 12px 18px;
        }}
        .brand {{ display: flex; align-items: center; gap: 12px; min-width: 0; font-weight: 800; }}
        .nav {{ display: flex; align-items: center; justify-content: flex-end; gap: 6px; flex-wrap: wrap; }}
        .nav a, .theme-toggle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 38px;
            padding: 0 12px;
            border: 1px solid transparent;
            border-radius: 8px;
            color: var(--muted);
            background: transparent;
            font: inherit;
            cursor: pointer;
        }}
        .nav a:hover, .theme-toggle:hover {{ color: var(--text); border-color: var(--border); background: var(--softer); }}
        .panel {{
            margin-top: 36px;
            padding: clamp(28px, 6vw, 58px);
        }}
        .eyebrow {{
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 0 10px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--softer);
            color: var(--muted);
            font-size: 13px;
            font-weight: 800;
        }}
        h1 {{
            max-width: 720px;
            margin: 18px 0 0;
            font-size: clamp(38px, 7vw, 72px);
            line-height: 1.02;
        }}
        .intro {{
            max-width: 680px;
            margin: 20px 0 0;
            color: var(--muted);
            font-size: 18px;
        }}
        .feed-box {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto auto;
            gap: 10px;
            align-items: center;
            margin-top: 34px;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--softer);
        }}
        .feed-url {{
            min-width: 0;
            overflow: auto;
            white-space: nowrap;
            padding: 0 4px;
            color: var(--text);
            font-family: "SFMono-Regular", Consolas, monospace;
            font-size: 14px;
        }}
        .button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 40px;
            padding: 0 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--soft);
            color: var(--text);
            font: inherit;
            font-weight: 800;
            cursor: pointer;
        }}
        .button.primary {{
            border-color: transparent;
            color: #fff;
            background: linear-gradient(135deg, #5271ff, #48c6ef);
        }}
        .button:hover {{ transform: translateY(-1px); }}
        .reader-list {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 30px 0 0;
            padding: 0;
            list-style: none;
        }}
        .reader-list a {{
            display: flex;
            align-items: center;
            min-height: 48px;
            padding: 0 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--softer);
            font-weight: 800;
        }}
        .reader-list a:hover {{ color: var(--accent); border-color: rgba(82, 113, 255, 0.45); }}
        footer {{ margin-top: 24px; color: rgba(255,255,255,.88); text-shadow: 0 1px 12px rgba(0,0,0,.24); font-size: 14px; }}
        @media (max-width: 760px) {{
            .feed-box {{ grid-template-columns: 1fr; }}
            .reader-list {{ grid-template-columns: 1fr; }}
        }}
        @media (max-width: 640px) {{
            .site-shell {{ width: calc(100% - 18px); padding-top: 14px; }}
            .topbar {{ align-items: flex-start; flex-direction: column; }}
            .nav {{ justify-content: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="site-shell">
        <header class="topbar">
            <a class="brand" href="./"><span>{SITE_TITLE}</span></a>
            <nav class="nav"><a href="./">主页</a><a href="tag.html">标签</a><a href="https://github.com/buwenjiayou" target="_blank" rel="noreferrer">GitHub</a><button class="theme-toggle" type="button" aria-label="切换明暗主题" onclick="toggleTheme()">☀</button></nav>
        </header>
        <main class="panel">
            <span class="eyebrow">RSS 订阅</span>
            <h1>把新文章交给阅读器</h1>
            <p class="intro">复制下面的订阅地址，添加到你常用的 RSS 阅读器。浏览器直接打开源文件时看到 XML 是正常现象，阅读器会自动解析成文章列表。</p>
            <div class="feed-box">
                <code class="feed-url" id="feedUrl">{feed_url}</code>
                <button class="button primary" type="button" id="copyButton">复制地址</button>
                <a class="button" href="rss.xml">打开源文件</a>
            </div>
            <ul class="reader-list" aria-label="常用 RSS 阅读器">
                <li><a href="https://www.inoreader.com/" target="_blank" rel="noreferrer">Inoreader</a></li>
                <li><a href="https://feedly.com/" target="_blank" rel="noreferrer">Feedly</a></li>
                <li><a href="https://hyliu.me/fluent-reader/" target="_blank" rel="noreferrer">Fluent Reader</a></li>
            </ul>
        </main>
        <footer>Copyright © <span id="copyrightYear"></span> {SITE_TITLE}</footer>
    </div>
    <script>
        const toggle = document.querySelector(".theme-toggle");
        function syncThemeIcon() {{
            toggle.textContent = document.documentElement.dataset.theme === "dark" ? "☾" : "☀";
        }}
        function toggleTheme() {{
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = nextTheme;
            localStorage.setItem("site-theme", nextTheme);
            syncThemeIcon();
        }}
        function fallbackCopy(text) {{
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.setAttribute("readonly", "");
            textarea.style.position = "fixed";
            textarea.style.left = "-9999px";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            textarea.remove();
        }}
        function setupCopyButton() {{
            const button = document.getElementById("copyButton");
            const feedUrl = document.getElementById("feedUrl").textContent.trim();
            button.addEventListener("click", async () => {{
                try {{
                    if (navigator.clipboard && window.isSecureContext) {{
                        await navigator.clipboard.writeText(feedUrl);
                    }} else {{
                        fallbackCopy(feedUrl);
                    }}
                    button.textContent = "已复制";
                    window.setTimeout(() => button.textContent = "复制地址", 1600);
                }} catch (error) {{
                    button.textContent = "手动复制";
                    window.setTimeout(() => button.textContent = "复制地址", 1600);
                }}
            }});
        }}
        document.getElementById("copyrightYear").textContent = new Date().getFullYear();
        syncThemeIcon();
        setupCopyButton();
    </script>
</body>
</html>
"""


def write_rss(posts: list[dict[str, object]]) -> None:
    items = []
    for post in posts[:20]:
        date = dt.datetime.fromisoformat(str(post["date"])).replace(tzinfo=dt.timezone.utc)
        url = f"{SITE_URL}/{post['url']}"
        items.append(
            f"""    <item>
      <title>{xml_escape(str(post["title"]))}</title>
      <link>{xml_escape(url)}</link>
      <guid isPermaLink="true">{xml_escape(url)}</guid>
      <description>{xml_escape(str(post["description"]))}</description>
      <pubDate>{format_datetime(date)}</pubDate>
    </item>"""
        )
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}/</link>
    <description>{SITE_DESCRIPTION}</description>
    <copyright>{SITE_TITLE}</copyright>
    <docs>http://www.rssboard.org/rss-specification</docs>
    <generator>scripts/build_posts.py</generator>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
{chr(10).join(items)}
  </channel>
</rss>
"""
    (DOCS_DIR / "rss.xml").write_text(rss, encoding="utf-8", newline="\n")


def clean_generated_posts() -> None:
    POST_DIR.mkdir(exist_ok=True)
    for html_file in POST_DIR.glob("*.html"):
        html_file.unlink()


def main() -> None:
    posts = read_posts()
    clean_generated_posts()
    for post in posts:
        (POST_DIR / f"{post['slug']}.html").write_text(render_post(post), encoding="utf-8", newline="\n")
    update_index(posts)
    (DOCS_DIR / "tag.html").write_text(render_tag_page(posts), encoding="utf-8", newline="\n")
    (DOCS_DIR / "rss.html").write_text(render_rss_page(), encoding="utf-8", newline="\n")
    write_post_list(posts)
    write_rss(posts)
    print(f"Generated {len(posts)} post(s).")


if __name__ == "__main__":
    main()
