class Connection:

    def __init__(self, responses=None):
        self.execs = list()

        self._resp_iter = None
        if responses is not None:
            self._resp_iter = iter(responses)

    def execute(self, method, adt_uri, headers=None, body=None):
        self.execs.append((method, adt_uri, headers, body))

        if self._resp_iter is not None:
            return next(self._resp_iter)

        return None
