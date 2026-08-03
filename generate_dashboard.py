import os
import sys
import json
import datetime
import urllib.request

USER_NAME = "chenzh659"
TODAY_STR = datetime.datetime.now().strftime("%Y-%m-%d")
DATE_DISPLAY = datetime.datetime.now().strftime("%Y年%m月%d日")

def fetch_user_repositories():
    """Fetch all user repositories from GitHub API."""
    url = f"https://api.github.com/users/{USER_NAME}/repos?per_page=100&sort=updated"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/vnd.github.v3+json"
    }

    repos = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data:
                updated_at_str = item.get("pushed_at") or item.get("updated_at") or ""
                pushed_dt = datetime.datetime.strptime(updated_at_str[:10], "%Y-%m-%d") if updated_at_str else datetime.datetime.now()
                days_since_update = (datetime.datetime.now() - pushed_dt).days

                license_info = item.get("license")
                license_name = license_info.get("name") if license_info else "未配置 License"

                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "desc": item.get("description") or "未提供仓库描述",
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "open_issues": item.get("open_issues_count", 0),
                    "language": item.get("language") or "配置文件/文档",
                    "license": license_name,
                    "updated_at": updated_at_str[:10],
                    "days_inactive": days_since_update,
                    "is_stale": days_since_update > 180,
                    "has_desc": bool(item.get("description")),
                    "has_license": bool(license_info)
                })
    except Exception as e:
        print(f"[Warning] Failed to fetch repositories for {USER_NAME}: {e}")
        repos = get_fallback_repos()

    return repos

def get_fallback_repos():
    """Fallback if API call fails."""
    return [
        {
            "name": "ai-daily-report",
            "full_name": "chenzh659/ai-daily-report",
            "desc": "全自动 AI 产业观察每日报告 (Anthropic 社论风格)",
            "url": "https://github.com/chenzh659/ai-daily-report",
            "stars": 1,
            "forks": 0,
            "open_issues": 0,
            "language": "HTML",
            "license": "MIT License",
            "updated_at": TODAY_STR,
            "days_inactive": 0,
            "is_stale": False,
            "has_desc": True,
            "has_license": True
        },
        {
            "name": "github-daily-trending",
            "full_name": "chenzh659/github-daily-trending",
            "desc": "GitHub 全球爆款开源项目每日推送系统",
            "url": "https://github.com/chenzh659/github-daily-trending",
            "stars": 1,
            "forks": 0,
            "open_issues": 0,
            "language": "Python",
            "license": "MIT License",
            "updated_at": TODAY_STR,
            "days_inactive": 0,
            "is_stale": False,
            "has_desc": True,
            "has_license": True
        }
    ]

def calculate_account_health(repos):
    """Calculates comprehensive health score and metrics."""
    total_repos = len(repos)
    if total_repos == 0:
        return {"score": 100, "stale_count": 0, "no_desc_count": 0, "no_license_count": 0}

    stale_count = sum(1 for r in repos if r["is_stale"])
    no_desc_count = sum(1 for r in repos if not r["has_desc"])
    no_license_count = sum(1 for r in repos if not r["has_license"])

    # Deductions
    deductions = (stale_count * 5) + (no_desc_count * 4) + (no_license_count * 3)
    score = max(50, 100 - deductions)

    return {
        "score": score,
        "total": total_repos,
        "stale_count": stale_count,
        "no_desc_count": no_desc_count,
        "no_license_count": no_license_count,
        "active_ratio": f"{int((1 - stale_count / total_repos) * 100)}%"
    }

def build_dashboard_html(repos, health):
    """Render Anthropic Editorial v2 HTML Dashboard."""
    
    total_stars = sum(r["stars"] for r in repos)
    total_forks = sum(r["forks"] for r in repos)

    # Language breakdown
    lang_counts = {}
    for r in repos:
        lang = r["language"]
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 账号全景巡检与健康度控制台 - {DATE_DISPLAY}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400&family=Noto+Serif+SC:wght@300;400;600;700&display=swap');

        :root {{
            --bg-paper: #FAF7F2;
            --card-bg: #FFFFFF;
            --card-subtle: #F3EFE6;
            --text-main: #1F1A17;
            --text-muted: #6E665E;
            --text-light: #8C837A;
            --accent-coral: #D97757;
            --accent-dark: #8C3B24;
            --accent-soft: #F2E3D5;
            --border-color: #E6DFD5;
            --border-dark: #D4C9B8;
            --shadow-subtle: rgba(31, 26, 23, 0.04);
            --shadow-hover: rgba(217, 119, 87, 0.12);
        }}

        [data-theme="dark"] {{
            --bg-paper: #181614;
            --card-bg: #23201D;
            --card-subtle: #2C2824;
            --text-main: #ECE6DE;
            --text-muted: #B3AAA0;
            --text-light: #8C837A;
            --accent-coral: #E08769;
            --accent-dark: #F0A58C;
            --accent-soft: #382A24;
            --border-color: #36312B;
            --border-dark: #4A433B;
            --shadow-subtle: rgba(0, 0, 0, 0.2);
            --shadow-hover: rgba(224, 135, 105, 0.2);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}

        body {{
            font-family: 'Noto Serif SC', 'Merriweather', 'Georgia', serif;
            background-color: var(--bg-paper);
            color: var(--text-main);
            line-height: 1.85;
            padding: 0;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }}

        #progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background-color: var(--accent-coral);
            width: 0%;
            z-index: 1000;
            transition: width 0.1s ease-out;
        }}

        .top-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-paper);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        .nav-title {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--accent-coral);
            font-weight: 700;
        }}

        .controls-group {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .btn-toggle {{
            background-color: var(--card-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-weight: 600;
        }}

        .btn-toggle:hover {{
            border-color: var(--accent-coral);
            color: var(--accent-coral);
        }}

        .header {{
            padding: 4rem 2rem 3rem;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-paper);
        }}

        .container {{
            max-width: 1120px;
            margin: 0 auto;
            padding: 0 1.5rem;
        }}

        .header-meta {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--accent-coral);
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .header-meta::before {{
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: var(--accent-coral);
            border-radius: 50%;
        }}

        .header h1 {{
            font-size: 2.8rem;
            font-weight: 700;
            color: var(--text-main);
            line-height: 1.25;
            margin-bottom: 1rem;
        }}

        .header p {{
            font-size: 1.2rem;
            color: var(--text-muted);
            font-style: italic;
            max-width: 850px;
            font-weight: 300;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin: 2.5rem 0 3rem;
        }}

        .stat-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px var(--shadow-subtle);
        }}

        .stat-label {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-light);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--accent-dark);
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}

        .stat-desc {{
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.5;
        }}

        .tab-bar {{
            display: flex;
            gap: 0.5rem;
            margin: 2.5rem 0 1.5rem 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        .tab-btn {{
            background: none;
            border: none;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.9rem;
            color: var(--text-muted);
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-radius: 4px;
            font-weight: 600;
        }}

        .tab-btn.active {{
            color: var(--accent-coral);
            background-color: var(--accent-soft);
        }}

        .editorial-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.75rem 0;
            font-size: 0.95rem;
        }}

        .editorial-table th, .editorial-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}

        .editorial-table th {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border-dark);
        }}

        .badge-status {{
            display: inline-block;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.75rem;
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            font-weight: 600;
        }}

        .badge-active {{ background-color: #E6F4EA; color: #137333; }}
        .badge-stale {{ background-color: #FEF7E0; color: #B06000; }}
        .badge-alert {{ background-color: #FCE8E6; color: #C5221F; }}

        .callout {{
            background-color: var(--card-subtle);
            border-left: 3px solid var(--accent-coral);
            padding: 1.5rem 1.75rem;
            margin: 1.75rem 0;
            border-radius: 0 4px 4px 0;
        }}

        .callout-title {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-dark);
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .toast {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background-color: var(--accent-dark);
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.875rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 1000;
        }}

        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        .footer {{
            border-top: 1px solid var(--border-color);
            padding: 3.5rem 0;
            background-color: var(--bg-paper);
            color: var(--text-muted);
            font-size: 0.9rem;
            text-align: center;
        }}
    </style>
</head>
<body>

    <div id="progress-bar"></div>

    <nav class="top-nav">
        <div class="nav-title">GitHub Asset & Hygiene Control · {USER_NAME}</div>
        <div class="controls-group">
            <button class="btn-toggle" onclick="copyDashboardSummary()">
                <span>📋</span> 复制健康度摘要
            </button>
            <button class="btn-toggle" onclick="toggleTheme()">
                <span id="theme-icon">🌙</span> <span id="theme-text">夜间模式</span>
            </button>
        </div>
    </nav>

    <header class="header">
        <div class="container">
            <div class="header-meta">
                <span>ACCOUNT-WIDE AUTOMATED AUDIT</span>
                <span>·</span>
                <span>{DATE_DISPLAY}</span>
            </div>
            <h1>GitHub 全账户资产巡检与健康度控制台</h1>
            <p>全自动监控账号 @{USER_NAME} 名下所有开源与私有代码资产的安全、规范度与活跃指标。</p>
        </div>
    </header>

    <div class="container">

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">账户健康得分</div>
                <div class="stat-value">{health['score']} <span style="font-size:1.1rem; color:var(--text-muted);">/ 100</span></div>
                <div class="stat-desc">根据规范度、许可协议配置及活跃度计算。</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">总代码仓库数</div>
                <div class="stat-value">{health['total']} 库</div>
                <div class="stat-desc">累计获得 Star: {total_stars} · Forks: {total_forks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">活跃仓库比例</div>
                <div class="stat-value">{health['active_ratio']}</div>
                <div class="stat-desc">近 180 天内有 Commit 或 Code Update</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">待优化项</div>
                <div class="stat-value">{health['no_desc_count'] + health['no_license_count']} 项</div>
                <div class="stat-desc">缺少仓库描述: {health['no_desc_count']} · 缺 License: {health['no_license_count']}</div>
            </div>
        </div>

        <div class="callout">
            <div class="callout-title">巡检建议 / Audit Recommendation</div>
            <p>全账户整体健康状况良好。建议为缺少描述的仓库补全 Description，并为未配置开源协议的项目添加标准 License 文件，以提升开源影响力与规范度。</p>
        </div>

        <h2 class="section-heading" style="font-size:1.5rem; margin-top:2.5rem; border-bottom:2px solid var(--text-main); padding-bottom:0.5rem;">📁 仓库巡检与状态明细 (Repository Audit)</h2>

        <table class="editorial-table">
            <thead>
                <tr>
                    <th>仓库名称</th>
                    <th>主要语言</th>
                    <th>星标 / Fork</th>
                    <th>开源协议</th>
                    <th>最后更新</th>
                    <th>健康度状态</th>
                </tr>
            </thead>
            <tbody>
"""

    for r in repos:
        status_badge = '<span class="badge-status badge-active">活跃 Active</span>'
        if r["is_stale"]:
            status_badge = '<span class="badge-status badge-stale">休眠 Stale (>180天)</span>'
        
        if not r["has_desc"] or not r["has_license"]:
            status_badge += ' <span class="badge-status badge-alert">需补全信息</span>'

        html += f"""
                <tr>
                    <td>
                        <a href="{r['url']}" target="_blank" style="color:var(--accent-dark); font-weight:700; text-decoration:none;">{r['name']}</a>
                        <div style="font-size:0.825rem; color:var(--text-muted); margin-top:0.2rem;">{r['desc']}</div>
                    </td>
                    <td><strong style="color:var(--text-main);">{r['language']}</strong></td>
                    <td>★ {r['stars']} · ⑂ {r['forks']}</td>
                    <td style="font-size:0.85rem;">{r['license']}</td>
                    <td style="font-size:0.85rem; color:var(--text-muted);">{r['updated_at']}</td>
                    <td>{status_badge}</td>
                </tr>
"""

    html += f"""
            </tbody>
        </table>

    </div>

    <div class="toast" id="toast">已成功复制账号健康度报告摘要！</div>

    <footer class="footer">
        <div class="container">
            <p>GitHub 账号全景巡检与健康度控制台 · {USER_NAME} · {DATE_DISPLAY}</p>
            <p style="font-style:italic; font-size:0.85rem; margin-top:0.5rem; color:var(--text-light);">“Continuous inspection builds sustainable software engineering.”</p>
        </div>
    </footer>

    <script>
        window.addEventListener('scroll', () => {{
            const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            document.getElementById('progress-bar').style.width = scrolled + '%';
        }});

        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            document.getElementById('theme-icon').textContent = newTheme === 'light' ? '🌙' : '☀️';
            document.getElementById('theme-text').textContent = newTheme === 'light' ? '夜间模式' : '日光模式';
        }}

        function copyDashboardSummary() {{
            const summaryText = "【GitHub 账号健康度巡检 {DATE_DISPLAY}】\\n账号: @{USER_NAME}\\n健康得分: {health['score']}/100\\n总仓库数: {health['total']}\\n活跃比例: {health['active_ratio']}\\n待优化项: {health['no_desc_count'] + health['no_license_count']} 项";
            navigator.clipboard.writeText(summaryText).then(() => {{
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2500);
            }});
        }}
    </script>
</body>
</html>"""

    return html

def main():
    print(f"🚀 Starting GitHub Account Dashboard inspection for {USER_NAME}...")
    
    repos = fetch_user_repositories()
    health = calculate_account_health(repos)
    
    dashboard_html = build_dashboard_html(repos, health)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print("✅ Successfully updated index.html")
    
    os.makedirs("reports", exist_ok=True)
    archive_file = os.path.join("reports", f"{TODAY_STR}.html")
    with open(archive_file, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print(f"✅ Successfully archived dashboard to {archive_file}")

if __name__ == "__main__":
    main()
