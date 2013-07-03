from gzip import GzipFile
from StringIO import StringIO
from noemie_format import NOEMIE

def noemie_try_gunzip(data):
    "gunzip data if its a gzip stream"
    sio = StringIO(data)
    gz = GzipFile(fileobj=sio, mode='rb')
    try:
        data = gz.read()
    except IOError:
        pass
    return data

def noemie_decode(data):
    lines = []
    entity = ''
    while data and entity != '999':
        entity = data[:3]
        analyzer = NOEMIE.get(entity)
        if analyzer is None:
            raise Exception('cannot analyse NOEMIE line "%s..."' % data[:32])
        line = { 'description': analyzer['description'] }
        segments = []
        index = 0
        for anaseg in analyzer.get('segments',[]):
            seg = {
                'name': anaseg['name'],
                }
            value = data[index : index+anaseg['size']]
            if anaseg.get('values'):
                seg['raw'] = value
                value = anaseg['values'].get(value)
            seg['value'] = value
            index += anaseg['size']
            segments.append(seg)
        line['segments'] = segments
        line['data'] = data[:index]
        data = data[index:]
        lines.append(line)
    return lines

if __name__ == '__main__':
    import sys
    from pprint import pprint
    data = noemie_try_gunzip(open(sys.argv[1]).read())
    pprint(noemie_decode(data), indent=2)
