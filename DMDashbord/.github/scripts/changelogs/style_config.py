class StyleConfig:
    # Type-specific colors and emojis
    TYPE_STYLES = {
        "feat": {"emoji": "✨", "color": "#2563eb"},    # Blue
        "fix": {"emoji": "🐛", "color": "#dc2626"},     # Red
        "docs": {"emoji": "📚", "color": "#7c3aed"},    # Purple
        "style": {"emoji": "💎", "color": "#db2777"},   # Pink
        "refactor": {"emoji": "♻️", "color": "#2dd4bf"},# Teal
        "perf": {"emoji": "⚡️", "color": "#f59e0b"},   # Amber
        "test": {"emoji": "🧪", "color": "#10b981"},    # Emerald
        "chore": {"emoji": "🔧", "color": "#6b7280"}    # Gray
    }

    # Priority order for commit types
    PRIORITY_ORDER = [
        'feat',     # New features first
        'fix',      # Bug fixes second
        'perf',     # Performance improvements
        'refactor', # Code refactoring
        'docs',     # Documentation changes
        'style',    # Style changes
        'test',     # Test changes
        'chore'     # Maintenance tasks last
    ]

    # Base styles for dark theme
    BASE_STYLES = """
        :root {
            --color-bg: #353543;
            --color-surface: #333355;
            --color-elevated: #3d3d4d;
            --color-text: #ffffff;
            --color-text-secondary: #e2e8f0;
            --color-border: rgba(255, 255, 255, 0.1);
            --radius-base: 8px;
            --radius-lg: 16px;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 8px rgba(0,0,0,0.3);
            --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--color-bg);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--color-text);
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background: linear-gradient(135deg, #333355 0%, #353543 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: var(--radius-lg);
            margin-bottom: 3rem;
            text-align: center;
            box-shadow: var(--shadow-md);
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #fff, #e2e8f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .type-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius-base);
            margin: 2rem 0 1rem;
            color: white;
            font-weight: 600;
            font-size: 1.25rem;
            transition: var(--transition);
        }

        .type-header:hover {
            transform: translateX(4px);
            filter: brightness(1.1);
        }

        .scope-tag {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--color-text);
            margin: 0.5rem 0;
            transition: var(--transition);
        }

        .scope-tag:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
            border-color: var(--color-text-secondary);
        }

        .commit-list {
            list-style: none;
            margin: 1rem 0;
        }

        .commit-item {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            padding: 1rem;
            margin-bottom: 1rem;
            transition: var(--transition);
        }

        .commit-item:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: var(--color-text-secondary);
            background: var(--color-elevated);
        }

        .commit-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--color-text);
        }

        .commit-meta {
            font-size: 0.875rem;
            color: var(--color-text-secondary);
            margin-top: 0.5rem;
        }

        .commit-body {
            background: var(--color-bg);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            padding: 1rem;
            margin: 0.5rem 0;
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 0.875rem;
        }

        details {
            margin: 1rem 0;
        }

        summary {
            cursor: pointer;
            margin-bottom: 1rem;
        }

        summary::-webkit-details-marker {
            display: none;
        }
    """
