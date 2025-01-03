from datetime import datetime

# data schemas for Pastebin API responses


class PasteDetails:
    """
    Metadata container for a Pastebin paste.
    """

    def __init__(
        self,
        paste_key: str,
        url: str,
        title: str,
        size: int,
        created_at: datetime,
        expires_at: datetime,
        visibility: str,
        highlighting: str,
        hits: int,
    ):
        self.paste_key = paste_key
        self.url = url
        self.name = title
        self.size = size
        self.created_at = created_at
        self.expires_at = expires_at
        self.visibility = visibility  # 'public', 'unlisted', or 'private'
        self.highlighting = highlighting  # e.g. 'python'
        self.hits = hits

    def __str__(self):
        return f"<PasteDetails: {self.name or 'Untitled'} at {self.url}>"


class UserDetails:
    """
    Metadata container for Pastebin user details and settings.
    """

    def __init__(
        self,
        username: str,
        avatar_url: str,
        default_highlighting: str,
        default_expiration: str,
        default_visibility: str,
        website: str,
        email: str,
        location: str,
        account_type: str,
    ):
        self.username = username
        self.avatar_url = avatar_url
        self.default_highlighting = default_highlighting  # e.g. 'python'
        self.default_expiration = default_expiration      # e.g. '10M', '1H'
        # 'public', 'unlisted', 'private'
        self.default_visibility = default_visibility
        self.website = website
        self.email = email
        self.location = location
        self.account_type = account_type                  # 'normal' or 'pro'

    def __str__(self):
        return f"<UserDetails: {self.username}>"
