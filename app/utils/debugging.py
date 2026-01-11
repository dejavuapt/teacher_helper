def init_debugpy(host: str, port: int):
    import debugpy
    debugpy.listen((host, port))
