class StyleConfig:
    # Type-specific colors and emojis
    TYPE_STYLES = {
        "feat": {"emoji": "✨", "color": "#1e90ff"},    # DodgerBlue
        "fix": {"emoji": "🐛", "color": "#ff4500"},     # OrangeRed
        "docs": {"emoji": "📚", "color": "#8a2be2"},    # BlueViolet
        "style": {"emoji": "💎", "color": "#ff69b4"},   # HotPink
        "refactor": {"emoji": "♻️", "color": "#20b2aa"},# LightSeaGreen
        "perf": {"emoji": "⚡️", "color": "#ffd700"},   # Gold
        "test": {"emoji": "🧪", "color": "#32cd32"},    # LimeGreen
        "chore": {"emoji": "🔧", "color": "#808080"}    # Gray
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

    # Base styles for modern light theme
    BASE_STYLES = """
:root {
    --color-bg: #ffffff;
    --color-surface: #ffffff;
    --color-elevated: #f0f0f0;
    --color-text: #000000;
    --color-text-secondary: #4a4a4a;
    --color-border: rgba(0, 0, 0, 0.1);
    --radius-base: 8px;
    --radius-lg: 16px;
    --shadow-sm: 0 2px 4px rgba(0,0,0,1);
    --shadow-md: 0 4px 8px rgba(0,0,0,0.2);
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
    color: black;
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
    color: black;
    font-weight: 600;
    font-size: 1.25rem;
    transition: var(--transition);
}

.type-header:hover {
    transform: translateX(4px);
    filter: brightness(0.9);
}

.scope-tag {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-base);
    font-size: 0.875rem;
    font-weight: 500;
    color: black !important; /* Ensure text is black */
    margin: 0.5rem 0;
    transition: var(--transition);
}

.scope-tag:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    border-color: var(--color-text-secondary);
    color: black !important; /* Ensure hover text remains black */
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
    position: relative;
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
    color: black !important; /* Ensure text is black */
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

.tags-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 1rem 0;
}

.tag-badge {
    background: var(--color-elevated);
    color: var(--color-text);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-base);
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid var(--color-border);
}

.copy-button {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: var(--color-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-base);
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    cursor: pointer;
    opacity: 0;
    transition: var(--transition);
}

.commit-item:hover .copy-button {
    opacity: 1;
}

.copy-button:hover {
    background: var(--color-surface);
    color: var(--color-text);
    border-color: var(--color-text-secondary);
}

.copy-button.copied {
    background: #10b981;
    color: white;
}

.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    border: 1px dashed var(--color-border);
    margin: 2rem 0;
}

.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}

.empty-state h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--color-text);
}

.empty-state p {
    color: var(--color-text-secondary);
}

/* Print-specific adjustments */
@media print {
    .scope-tag, .commit-title {
        color: black !important; /* Ensure colors remain black in PDFs */
    }
}
    """

    @staticmethod
    def generate_tag_badges(latest_tag: str, previous_tag: str) -> str:
        return f"""
        <div class="tags-container">
            <span class="tag-badge">Latest: {latest_tag}</span>
            <span class="tag-badge">Previous: {previous_tag}</span>
        </div>
        """