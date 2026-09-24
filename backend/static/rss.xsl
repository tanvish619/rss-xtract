<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:media="http://search.yahoo.com/mrss/">

  <xsl:output method="html" version="5.0" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title><xsl:value-of select="/rss/channel/title"/> — RSS Feed</title>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
        <style>
          *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

          :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #111118;
            --bg-card: #16161f;
            --bg-card-hover: #1c1c28;
            --border: rgba(255,255,255,0.07);
            --border-accent: rgba(139,92,246,0.35);
            --text-primary: #f0f0ff;
            --text-secondary: #9898b8;
            --text-muted: #5a5a78;
            --accent: #8b5cf6;
            --accent-2: #06b6d4;
            --accent-3: #f59e0b;
            --glow: rgba(139,92,246,0.15);
          }}

          html {{ scroll-behavior: smooth; }}

          body {{
            font-family: 'Inter', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
          }}

          /* ── Header ── */
          .site-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(10,10,15,0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 0 clamp(1rem, 5vw, 3rem);
          }}

          .header-inner {{
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 1rem;
            height: 64px;
          }}

          .rss-icon {{
            width: 32px; height: 32px; flex-shrink: 0;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 0 16px var(--glow);
          }}

          .header-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }}

          .header-badge {{
            margin-left: auto;
            flex-shrink: 0;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--accent);
            background: rgba(139,92,246,0.1);
            border: 1px solid rgba(139,92,246,0.25);
            padding: 4px 10px;
            border-radius: 999px;
          }}

          /* ── Hero ── */
          .hero {{
            padding: clamp(2.5rem, 6vw, 4rem) clamp(1rem, 5vw, 3rem) clamp(2rem, 5vw, 3rem);
            max-width: 900px;
            margin: 0 auto;
          }}

          .hero-eyebrow {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--accent-2);
            margin-bottom: 0.75rem;
          }}

          .hero-title {{
            font-size: clamp(1.75rem, 4vw, 2.75rem);
            font-weight: 700;
            line-height: 1.15;
            background: linear-gradient(120deg, var(--text-primary) 0%, var(--text-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
          }}

          .hero-desc {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin-bottom: 1.75rem;
          }}

          .hero-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
          }}

          .hero-meta span {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
          }}

          .hero-divider {{
            border: none;
            border-top: 1px solid var(--border);
            max-width: 900px;
            margin: 0 auto 2rem;
          }}

          /* ── Feed list ── */
          .feed-list {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 clamp(1rem, 5vw, 3rem) clamp(3rem, 8vw, 5rem);
            display: flex;
            flex-direction: column;
            gap: 1px;
          }}

          .feed-item {{
            position: relative;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
            margin-bottom: 10px;
            overflow: hidden;
          }}

          .feed-item::before {{
            content: '';
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: linear-gradient(135deg, rgba(139,92,246,0.05) 0%, transparent 60%);
            opacity: 0;
            transition: opacity 0.18s ease;
            pointer-events: none;
          }}

          .feed-item:hover {{
            transform: translateY(-2px);
            border-color: var(--border-accent);
            background: var(--bg-card-hover);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(139,92,246,0.1);
          }}

          .feed-item:hover::before {{ opacity: 1; }}

          .item-category {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--accent-2);
            background: rgba(6,182,212,0.08);
            border: 1px solid rgba(6,182,212,0.2);
            padding: 3px 9px;
            border-radius: 999px;
            margin-bottom: 0.65rem;
          }}

          .item-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.4;
            margin-bottom: 0.5rem;
          }}

          .item-title a {{
            color: inherit;
            text-decoration: none;
            transition: color 0.15s ease;
          }}

          .item-title a:hover {{ color: var(--accent); }}

          .item-desc {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            line-height: 1.55;
            margin-bottom: 0.9rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }}

          .item-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
          }}

          .item-author {{
            font-size: 0.78rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 0.35rem;
          }}

          .item-read-link {{
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--accent);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            padding: 5px 12px;
            border-radius: 6px;
            background: rgba(139,92,246,0.08);
            border: 1px solid rgba(139,92,246,0.2);
            transition: background 0.15s, border-color 0.15s, color 0.15s;
          }}

          .item-read-link:hover {{
            background: rgba(139,92,246,0.18);
            border-color: rgba(139,92,246,0.45);
            color: #c4b5fd;
          }}

          /* ── Empty state ── */
          .empty-state {{
            text-align: center;
            padding: 5rem 2rem;
            color: var(--text-muted);
          }}

          .empty-icon {{ font-size: 3rem; margin-bottom: 1rem; }}
          .empty-msg {{ font-size: 1rem; }}

          /* ── Footer ── */
          .site-footer {{
            border-top: 1px solid var(--border);
            padding: 1.25rem clamp(1rem, 5vw, 3rem);
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
          }}

          .site-footer a {{
            color: var(--accent);
            text-decoration: none;
          }}

          /* ── Scrollbar ── */
          ::-webkit-scrollbar {{ width: 6px; }}
          ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
          ::-webkit-scrollbar-thumb {{ background: #2a2a40; border-radius: 3px; }}
          ::-webkit-scrollbar-thumb:hover {{ background: #3a3a58; }}
        </style>
      </head>
      <body>

        <!-- Header -->
        <header class="site-header">
          <div class="header-inner">
            <div class="rss-icon">&#x25A3;</div>
            <span class="header-title"><xsl:value-of select="/rss/channel/title"/></span>
            <span class="header-badge">RSS Feed</span>
          </div>
        </header>

        <!-- Hero -->
        <section class="hero">
          <p class="hero-eyebrow">&#x2605; Live Feed</p>
          <h1 class="hero-title"><xsl:value-of select="/rss/channel/title"/></h1>
          <p class="hero-desc"><xsl:value-of select="/rss/channel/description"/></p>
          <div class="hero-meta">
            <span>
              &#x1F517;&#xFE0F; <xsl:value-of select="/rss/channel/link"/>
            </span>
            <xsl:if test="/rss/channel/lastBuildDate">
              <span>
                &#x1F504; Updated: <xsl:value-of select="/rss/channel/lastBuildDate"/>
              </span>
            </xsl:if>
            <span>
              &#x1F4F0; <xsl:value-of select="count(/rss/channel/item)"/> articles
            </span>
          </div>
        </section>

        <hr class="hero-divider"/>

        <!-- Items -->
        <main class="feed-list">
          <xsl:choose>
            <xsl:when test="/rss/channel/item">
              <xsl:for-each select="/rss/channel/item">
                <article class="feed-item">
                  <xsl:if test="category">
                    <div class="item-category">
                      &#x25C6; <xsl:value-of select="category"/>
                    </div>
                  </xsl:if>
                  <h2 class="item-title">
                    <a>
                      <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                      <xsl:attribute name="target">_blank</xsl:attribute>
                      <xsl:attribute name="rel">noopener noreferrer</xsl:attribute>
                      <xsl:value-of select="title"/>
                    </a>
                  </h2>
                  <xsl:if test="description and description != title">
                    <p class="item-desc"><xsl:value-of select="description"/></p>
                  </xsl:if>
                  <div class="item-footer">
                    <xsl:if test="author">
                      <span class="item-author">
                        &#x270D; <xsl:value-of select="author"/>
                      </span>
                    </xsl:if>
                    <a class="item-read-link">
                      <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                      <xsl:attribute name="target">_blank</xsl:attribute>
                      <xsl:attribute name="rel">noopener noreferrer</xsl:attribute>
                      Read article &#x2192;
                    </a>
                  </div>
                </article>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <div class="empty-state">
                <div class="empty-icon">&#x1F4ED;</div>
                <p class="empty-msg">No articles found in this feed yet.</p>
              </div>
            </xsl:otherwise>
          </xsl:choose>
        </main>

        <!-- Footer -->
        <footer class="site-footer">
          Powered by <a href="/">RSS Xtract</a> &#x2022; Subscribe by copying this page URL into your RSS reader
        </footer>

      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
