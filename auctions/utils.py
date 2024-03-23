def build_comment_tree(comments):
    """
    Recursively builds a nested dictionary of comments and their replies.
    """
    comment_tree = {}
    for comment in comments:
        comment_tree[comment] = build_comment_tree(comment.replies.all())
    return comment_tree