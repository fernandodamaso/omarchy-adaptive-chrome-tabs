class FakeClock:
    def __init__(self, start_ms=0):
        self.now_ms = start_ms

    def advance(self, milliseconds):
        if milliseconds < 0:
            raise ValueError("fake monotonic clock cannot move backwards")
        self.now_ms += milliseconds
        return self.now_ms


class FakeAdapterSink:
    def __init__(self):
        self.requests = []

    def record(self, request):
        self.requests.append(request)
        return request

    def complete(self, policy, request, clock, actual_orientation=None):
        return policy.verify(request, actual_orientation or request.orientation, clock.now_ms)

    def apply_and_verify(self, policy, request, clock, actual_orientation=None):
        self.record(request)
        return self.complete(policy, request, clock, actual_orientation)
