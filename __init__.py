def classFactory(iface):
    from .memorial_plugin import MemorialPlugin
    return MemorialPlugin(iface)
