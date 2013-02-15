import os
import subprocess
import tempfile

class PdfTk(object):
    def __init__(self, pdftk_path=None, prefix='tmp'):
        self._pdftk_path = pdftk_path
        self.prefix = prefix

    @property
    def pdftk_path(self):
        return self._pdftk_path or '/usr/bin/pdftk'

    def do(self, args, wait=True):
        args = [self.pdftk_path] + args
        proc = subprocess.Popen(args)
        if wait:
            return proc.wait()
        else:
            return proc

    def concat(self, input_files, output_file, wait=True):
        args = input_files + ['cat', 'output', output_file, 'compress', 'flatten']
        return self.do(args, wait=wait)

    def background(self, input_file, background_file, output_file, wait=True):
        args = [input_file, 'background', background_file, 'output', output_file, 'compress']
        return self.do(args, wait=wait)


if __name__ == '__main__':
    import sys

    pdftk = PdfTk()
    if sys.argv[1] == 'concat':
        pdftk.concat(sys.argv[2].split(','), sys.argv[3])
    elif sys.argv[1] == 'background':
        pdftk.background(*sys.argv[2:5])
    else:
        raise RuntimeError('Unknown command %s', sys.argv)
