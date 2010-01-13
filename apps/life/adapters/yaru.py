def adapt_ya_text(feedpost):
    """
    Adapt Ya.ru items to show only texts
    (not links, moods, images or videos)
    """
    if feedpost['tags'] and 'ya.ru:text' in feedpost['tags']:
        return feedpost

