from enum import Enum
from subprocess import PIPE
from os.path import join, splitext, basename
import config.config as config
import psutil
import glob


class ConversionStatus(Enum):
    running = 'running'
    success = 'success'
    fail = 'fail'


class ConversionProcess:
    def __init__(self, filename):
        self.filename = filename
        self.status = None
        self.run_count = 0

        self.stdout = ''
        self.stderr = ''

        self._process = None
        self._return_code = None
        self._finished = False

    def run(self):
        self._process = psutil.Popen(
            [str(config.READW_SCRIPT_PATH), self.filename],
            stdout=PIPE,
            stderr=PIPE
        )

        self.stdout = ''
        self.stderr = ''
        self.run_count += 1
        self._return_code = None
        self.status = ConversionStatus.running


    def poll(self):
        # do not poll unnecessarily
        if self._finished:
            return

        # updating status of conversion depending on return code
        try:
            return_code = self._process.poll()
            self._return_code = return_code

            if return_code == None:
                self.status = ConversionStatus.running
            elif return_code == 0:
                self.status = ConversionStatus.success
                self._update_std_outputs()
                self._process.terminate()
            elif self.run_count < config.NUM_RETRIES + 1:
                self.run()
            else:
                self._update_std_outputs()
                self._finished = True
                self.status = ConversionStatus.fail
        except:
            # process is no longer around to be polled
            self._finished = True
            pass

    def _update_std_outputs(self):
        self.stdout = self._process.stdout.read().decode('utf-8')
        self.stderr = self._process.stderr.read().decode('utf-8')

    def abort(self):
        try:
            self._process.kill()
            self.status = ConversionStatus.fail
            self._finished = True
        except:
            pass

    @property
    def summary(self):
        return {
            'filename:': self.filename,
            'status': self.status.value,
            'run_count': self.run_count,
            'stdout': self.stdout,
            'stderr': self.stderr
        }

    def __repr__(self):
        return 'ConversionProcess(filename={}, status={}, run_count={})'.format(
            self.filename,
            self.status,
            str(self.run_count)
        )


class NoRawFilesException(Exception):
    pass


def convert_folder(path):
    raw_files = list(glob.iglob(join(config.RAW_VAULT, path, '*.RAW')))

    # make sure the given path contains raw files
    if not len(raw_files): raise NoRawFilesException

    conversions = []

    for item in raw_files:
        conv = ConversionProcess(item)
        conv.run()
        conversions.append(conv)

    return conversions
