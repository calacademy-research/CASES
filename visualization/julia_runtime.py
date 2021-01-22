from singleton_decorator import singleton
not used?
@singleton
class JuliaRuntime:
    def __init__(self):
        # from julia import Main as j
        from julia.api import Julia
        jl = Julia(compiled_modules=False)
        from julia import Main as j

        self.julia_runtime = j

    def get(self):
        return JuliaSingleton.instance.j