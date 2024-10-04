from uuid import uuid4
from typing import Dict, Any

from django_components import component  # type: ignore[import]
from apps.shopping.common import resolve_active_menu_item


@component.register(name="menu_collapse")
class MenuCollapse(component.Component):
    template_name = "menu_collapse/menu_collapse.html"

    def get_context_data(self, request, url_names: str | None = None, *args, **kwargs) -> Dict[str, Any]:
        active = False
        if url_names:
            active = resolve_active_menu_item(request, url_names)
        return {
            "active": active,
            "collapse_id": "x" + uuid4().hex,  # first symbol must be a letter
            "args": args,
            "kwargs": kwargs,
        }
