import grpc


class InstantFuture(grpc.Future):
    def __init__(self, resp):
        self.resp = resp

    def cancel(self):
        return False

    def cancelled(self):
        return False

    def running(self):
        return False

    def done(self):
        return True

    def result(self, timeout=None):
        return self.resp

    def exception(self, timeout=None):
        return None

    def traceback(self, timeout=None):
        return None

    def add_done_callback(self, fn):
        fn(self)
