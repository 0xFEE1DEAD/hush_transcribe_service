"""Exceptions for media module."""


class MediaModuleError(Exception):
    """Base error class for media module."""


class MediaUnknownError(MediaModuleError):
    """Unknown error."""


class MediaFileNotFoundError(MediaModuleError):
    """File does not exists or wrong."""


class MediaFileCanNotBeReadError(MediaModuleError):
    """Media file can not be read."""
