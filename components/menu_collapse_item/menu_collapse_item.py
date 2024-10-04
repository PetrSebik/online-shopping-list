from typing import Dict, Any

from django_components import component  # type: ignore[import]


@component.register(name="menu_collapse_item")
class MenuCollapseItem(component.Component):
    template_name = "menu_collapse_item/menu_collapse_item.html"

    def get_context_data(self, label: str = 'placeholder', redirect_to: str = 'dashboard',
                         *args, **kwargs) -> Dict[str, Any]:
        return {
            "label": label,
            "redirect_to": redirect_to,
            "args": args,
            "kwargs": kwargs,
        }
