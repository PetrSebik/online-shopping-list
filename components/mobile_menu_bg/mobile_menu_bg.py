from typing import Any, Dict

from django_components import component  # type: ignore[import]


@component.register(name="mobile_menu_bg")
class MobileMenuBg(component.Component):
    template_name = "mobile_menu_bg/mobile_menu_bg.html"

    def get_context_data(self,) -> Dict[str, Any]:
        return {}

    class Media:
        css = "mobile_menu_bg/mobile_menu_bg.css"
        js = "mobile_menu_bg/mobile_menu_bg.js"
