from datetime import datetime
import json

# data schemas for Pastebin API responses


class PasteDetails:
    """
    Metadata container for a Pastebin paste.
    """

    def __init__(
        self,
        key: str,
        url: str,
        title: str,
        size: int,
        created_at: datetime,
        expires_at: datetime,
        visibility: str,
        highlighting: str,
        hits: int,
    ):
        self.key = key
        self.url = url
        self.name = title
        self.size = size
        self.created_at = created_at
        self.expires_at = expires_at
        self.visibility = visibility  # 'public', 'unlisted', or 'private'
        self.highlighting = highlighting  # e.g. 'python'
        self.hits = hits

    def to_dict(self):
        """
        Convert the PasteDetails object to a dictionary.
        """
        return {
            "key": self.key,
            "url": self.url,
            "title": self.name,
            "size": self.size,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "visibility": self.visibility,
            "highlighting": self.highlighting,
            "hits": self.hits,
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


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

    def to_dict(self):
        """
        Convert the UserDetails object to a dictionary.
        """
        return {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "default_highlighting": self.default_highlighting,
            "default_expiration": self.default_expiration,
            "default_visibility": self.default_visibility,
            "website": self.website,
            "email": self.email,
            "location": self.location,
            "account_type": self.account_type,
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)
