# apps/chat/templatetags/markdown_filters.py

from django import template
from markdown import markdown
import bleach
import re

register = template.Library()


@register.filter(name='markdown_to_html')
def markdown_to_html(value):
    # Convert markdown to HTML
    html = markdown(value, extensions=['fenced_code', 'tables'])

    # Sanitize the HTML to prevent XSS attacks
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'strong', 'em',
                    'ul', 'ol', 'li', 'code', 'pre', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
    allowed_attributes = {'*': ['class']}
    clean_html = bleach.clean(html, tags=allowed_tags,
                              attributes=allowed_attributes)

    # Replace &lt; and &gt; within <pre> tags
    clean_html = re.sub(r'<pre><code>(.*?)</code></pre>', lambda m: '<pre><code>' + m.group(
        1).replace('&lt;', '<').replace('&gt;', '>') + '</code></pre>', clean_html, flags=re.DOTALL)

    return clean_html
