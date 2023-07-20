import contextlib
import signal
import sys


class ExitOnDoubleInterrupt(contextlib.AbstractContextManager):
    """A context manager which exits the application on SIGINT.

    The first interrupt waits for the operation to finish and then exits.
    The second interrupt exits immediately.
    """
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.was_interrupted = False
        # swap interrupt handler for a custom one
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
        return self

    def handler(self, sig, frame):
        # delay the first interrupt
        if not self.was_interrupted:
            self.was_interrupted = True
            print(self.message, file=sys.stderr)
        # propagate the second interrupt
        else:
            signal.signal(signal.SIGINT, self.old_handler)
            raise KeyboardInterrupt

    def __exit__(self, *excinfo):
        signal.signal(signal.SIGINT, self.old_handler)

        if self.was_interrupted:
            sys.exit()
