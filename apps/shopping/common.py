
def resolve_active_menu_item(request, url_names: str) -> bool:
    url_names_list = url_names.split(',') if ',' in url_names else [url_names, ]
    resolver_match = request.resolver_match
    if resolver_match and resolver_match.url_name in url_names_list:
        return True
    return False
