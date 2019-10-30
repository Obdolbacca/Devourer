from subprocess import PIPE, STDOUT, Popen
from typing import Union, Optional, Tuple
from threading import Thread
from time import sleep
from .watchdog_timer import WatchdogTimer


class OutputDevourer(Thread):
    def __init__(self, command: Union[bytes, str],
                 pipe_name: Union[bytes, str] = '/var/run/devourer.pipe',
                 time_to_wait: int = 5):
        self._command = command
        self._timeout = time_to_wait
        self._pipe_name = pipe_name
        self._subproc: Optional[Thread] = None
        self.message: str = ''
        self._event_type = None
        self._capture_output = True
        super(OutputDevourer, self).__init__()

    def run(self):
        self._subproc = Thread(target=self._create_subproc)
        self._subproc.start()
        sleep(self._timeout * 1.0)

    def finalize(self):
        self._event_type = 'kill'
        self._subproc.join(2.0)
        self.join(2.0)
        return self.message

    def _create_subproc(self):
        with Popen(self._command, stdout=PIPE, stderr=STDOUT,
                   universal_newlines=True, shell=True) as process:  # text mode
            # kill process in timeout seconds unless the timer is restarted
            watchdog = WatchdogTimer(self._timeout, args=process, callback=self._event, daemon=True)
            watchdog.start()
            for line in process.stdout:
                # don't invoke the watcthdog callback if do_something() takes too long
                with watchdog.blocked:
                    if self._capture_output:
                        self.message += line  # some criterium is not satisfied
                    else:
                        pass
            watchdog.cancel()

    def _event(self, *args):
        if not self._event_type:
            self._capture_output = False
        else:
            process = args[0]
            process.kill()


def spawn(command: Union[bytes, str],
          pipe_name: Union[bytes, str] = '/var/run/devourer.pipe',
          time_to_wait: int = 3) -> OutputDevourer:
    devourer = OutputDevourer(command, pipe_name, time_to_wait)
    devourer.start()
    return devourer
