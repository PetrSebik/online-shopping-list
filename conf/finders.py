from typing import List, Union

from django_components.finders import ComponentsFileSystemFinder


class CompatComponentsFileSystemFinder(ComponentsFileSystemFinder):
    """Bridge django-components 0.101's finder to Django 5.x's ``find_all`` kwarg.

    Django 5.0 renamed the ``find()`` parameter ``all`` -> ``find_all``. The
    pinned django-components release still defines ``find(self, path, all=False)``,
    so when Django serves a component's static file it calls it with
    ``find_all=...`` and the finder raises ``TypeError`` (HTTP 500). This was
    breaking the mobile menu's JS/CSS. Accept both spellings and delegate.
    """

    def find(self, path: str, find_all: bool = False, **kwargs) -> Union[List[str], str]:
        all_ = kwargs.pop("all", find_all)
        return super().find(path, all=all_)
