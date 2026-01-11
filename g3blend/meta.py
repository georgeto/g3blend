def get_addon_version() -> tuple[int, int, int]:
    from . import bl_info  # noqa: PLC0415 Avoid circular import

    return bl_info['version']
