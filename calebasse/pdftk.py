import subprocess
import tempfile

from fdfgen import forge_fdf

class PdfTk(object):
    def __init__(self, pdftk_path=None):
        self._pdftk_path = pdftk_path

    @property
    def pdftk_path(self):
        return self._pdftk_path or '/usr/bin/pdftk'

    def do(self, args):
        print 'do', args
        args = [self.pdftk_path] + args
        proc = subprocess.Popen(args)
        return proc.wait()

    def concat(self, input_files, output_file):
        args = input_files + ['cat', 'output', output_file]
        return self.do(args)

    def form_fill(self, pdf_file, fields, output_file, flatten=False):
        string_fields = []
        other_fields = []
        # separate string from booleans
        for k, v in fields.iteritems():
            if isinstance(k, basestring):
                string_fields.append((k, v))
            else:
                other_fields.append((k[0], k[1] if isinstance(v, bool) else v))
        with tempfile.NamedTemporaryFile() as temp_fdf:
            fdf = forge_fdf("", string_fields, other_fields, [], [])
            temp_fdf.write(fdf)
            temp_fdf.flush()
            args = [pdf_file, 'fill_form', temp_fdf.name, 'output', output_file]
            if flatten:
                args.insert(3, 'flatten')
            result = self.do(args)
            temp_fdf.close()
            return result

if __name__ == '__main__':
    import sys

    pdftk = PdfTk()
    if sys.argv[1] == 'concat':
        pdftk.concat(sys.argv[2].split(','), sys.argv[3])
    elif sys.argv[1] == 'fill':
        fields = sys.argv[3].split(',')
        fields = zip(fields[0::2], fields[1::2])
        pdftk.form_fill(sys.argv[2], dict(fields), sys.argv[4])
    else:
        raise RuntimeError('Unknown command %s', sys.argv)
