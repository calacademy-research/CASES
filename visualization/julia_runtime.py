from singleton_decorator import singleton

@singleton
class JuliaRuntime:
    def __init__(self):
        from julia import Main as j
        self.julia_runtime = j

    def get(self):
        return JuliaSingleton.instance.j