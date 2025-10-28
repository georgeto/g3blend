def get_addon_version() -> tuple[int, int, int]:
    from . import bl_info
    return bl_info['version']
