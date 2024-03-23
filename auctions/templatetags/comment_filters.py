from django import template

register = template.Library()

@register.filter
def get_replies(comments_tree, comment):
    """Retrieve replies for a specific comment from the comments_tree."""
    return comments_tree.get(comment, {})
