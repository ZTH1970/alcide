#!/usr/bin/python
from setuptools import setup, find_packages
import os

def get_version():
    import glob
    import re
    import os

    version = None
    for d in glob.glob('*'):
        if not os.path.isdir(d):
            continue
        module_file = os.path.join(d, '__init__.py')
        if not os.path.exists(module_file):
            continue
        for v in re.findall("""__version__ *= *['"](.*)['"]""",
                open(module_file).read()):
            assert version is None
            version = v
        if version:
            break
    assert version is not None
    if os.path.exists('.git'):
        import subprocess
        p = subprocess.Popen(['git','describe','--dirty'],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        assert p.returncode == 0, 'git returned non-zero'
        new_version = result.split()[0]
        assert new_version.split('-')[0] == version, '__version__ must match the last git annotated tag'
        version = new_version.replace('-', '.')
    return version


setup(name='calebasse',
        version=get_version(),
        license='AGPLv3',
        description='',
        url='http://dev.entrouvert.org/projects/calebasse/',
        download_url='http://repos.entrouvert.org/calebasse.git/',
        author="Entr'ouvert",
        author_email="info@entrouvert.com",
        packages=find_packages(os.path.dirname(__file__) or '.'),
        install_requires=[
            'django >= 1.4.2, < 1.5',
            'south >= 0.7',
            'django-reversion >= 1.6.4',
            'python-dateutil >=1.5, < 2.0',
            'django-model-utils < 1.2.0',
            'django-ajax-selects < 1.3.0',
            'django-widget-tweaks < 1.2.0',
            'django-tastypie >= 0.9, < 1.0',
            'interval == 1.0.0',
            'python-entrouvert >= 1.3'
            'django-debug-toolbar',
        ],
        dependency_links = [
            'http://django-swingtime.googlecode.com/files/django-swingtime-0.2.1.tar.gz#egg=django-swingtime-0.2.1',
        ],
)
