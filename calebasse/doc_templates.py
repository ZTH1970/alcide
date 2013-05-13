import os
import os.path
import re
import contextlib
import tempfile

__ALL__ = [ 'DocTemplateError', 'make_doc_from_template' ]

VARIABLE_RE = re.compile(r'@[A-Z]{2,3}[0-9]{0,2}')

class DocTemplateError(RuntimeError):
    def __str__(self):
        return ' '.join(map(str, self.args))


@contextlib.contextmanager
def delete_on_error(f):
    '''Context manager which deletes a file if an exception occur'''
    try:
        yield
    except:
        os.remove(f.name)
        raise


def replace_variables(template, variables, ignore_unused=True):
    '''Lookup all substring looking like @XXX9 in the string template, and
       replace them by the value of the key XXX9 in the dictionary variables.

       Returns a new :class:str

       :param template: string containing the variables references
       :param variables: dictionary containing the variables values

    '''
    needed_vars = set([v[1:] for v in re.findall(VARIABLE_RE, template)])
    given_vars = set(variables.keys())
    if given_vars != needed_vars:
        missing = needed_vars - given_vars
        if missing or not ignore_unused:
            unused = given_vars - needed_vars
            raise DocTemplateError(
                'Mismatch between given and needed variables: missing={0} unused={1}'
                .format(map(repr, missing), map(repr, unused)))
    def variable_replacement(match_obj):
        return variables[match_obj.group(0)[1:]]
    return re.sub(VARIABLE_RE, variable_replacement, template)


def char_to_rtf(c):
    if ord(c) < 128:
        return c
    else:
        return '\u%d?' % ord(c)


def utf8_to_rtf(s):
    s = ''.join([ char_to_rtf(c) for c in s])
    return '{\uc1{%s}}' % s


def unicode_to_rtf(value):
    try:
        value = unicode(value)
    except Exception, e:
        raise DocTemplateError('Unable to get a unicode value', e)
    return utf8_to_rtf(value)


def variables_to_rtf(variables):
    return dict(((k, unicode_to_rtf(v)) for k,v in variables.iteritems()))


def make_doc_from_template(from_path, to_path, variables, persistent):
    '''Use file from_path as a template to combine with the variables
       dictionary and place the result in the file to_path.
       Encode value of variable into encoding of UTF-8 for the RTF file format.

       :param from_path: the template file path
       :param to_path: the newly created file containing the result of the templating
       :param variables: the dictionary of variables to replace
    '''

    if not os.path.exists(from_path):
        raise DocTemplateError('Template file does not exist', repr(from_path))
    if os.path.exists(to_path):
        raise DocTemplateError('Destination file already exists', repr(to_path))
    variables = variables_to_rtf(variables)
    if persistent:
        with open(to_path, 'w') as to_file:
            with open(from_path) as from_file:
                with delete_on_error(to_file):
                    to_file.write(replace_variables(from_file.read(), variables))
    else:
        with tempfile.NamedTemporaryFile(prefix=to_path,
                delete=False) as to_file:
            with open(from_path) as from_file:
                with delete_on_error(to_file):
                    to_file.write(replace_variables(from_file.read(), variables))
    return to_file.name

if __name__ == '__main__':
    import sys
    try:
        variables = dict((map(lambda x: unicode(x, 'utf-8'), arg.split('=')) for arg in sys.argv[3:]))
        make_doc_from_template(sys.argv[1], sys.argv[2], variables)
    except Exception, e:
        raise
        print 'Usage: python doc_template.py <template.rtf> <output.rtf> [KEY1=value1 KEY2=value2 ...]'
