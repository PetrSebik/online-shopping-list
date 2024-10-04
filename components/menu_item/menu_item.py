from typing import Dict, Any

from django_components import component  # type: ignore[import]
from apps.shopping.common import resolve_active_menu_item


@component.register(name="menu_item")
class MenuItem(component.Component):
    template_name = "menu_item/menu_item.html"

    def get_context_data(self, request, redirect_to: str = 'dashboard',
                         url_names: str | None = None, pk_kwarg: str | None = None,
                         *args, **kwargs) -> Dict[str, Any]:
        active = False
        if url_names:
            active = resolve_active_menu_item(request, url_names)

        return {
            "redirect_to": redirect_to,
            "active": active,
            "pk_kwarg": pk_kwarg,
            "args": args,
            "kwargs": kwargs,
        }
