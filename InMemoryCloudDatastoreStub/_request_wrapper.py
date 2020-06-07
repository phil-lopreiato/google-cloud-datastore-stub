import grpc
from .futures import InstantFuture


class _RequestWrapper(grpc.UnaryUnaryMultiCallable):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args, **kwargs):
        return self.func(request, *args, **kwargs)

    def with_call(self, request, *args, **kwargs):
        return self(request, *args, **kwargs)

    def future(self, request, *args, **kwargs):
        resp = self(request, *args, **kwargs)
        return InstantFuture(resp)
