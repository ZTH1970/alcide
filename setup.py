#!/usr/bin/python
from setuptools import setup, find_packages
import os

def get_version():
    from alcide import __version__
    version = __version__
    if os.path.exists('.git'):
        import subprocess
        p = subprocess.Popen(['git','describe','--dirty','--match=v*'],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        assert p.returncode == 0, 'git returned non-zero'
        new_version = result.split()[0][1:]
        assert new_version.split('-')[0] == version, '__version__ must match the last git annotated tag'
        version = new_version.replace('-', '.')
    return version


setup(name='alcide',
        version=get_version(),
        license='AGPLv3',
        description='',
        url='https://github.com/ZTH1970/alcide',
        download_url='https://github.com/ZTH1970/alcide.git',
        author="Paradis Charlotte &",
        author_email="paradischarlotte93@gmail.com",
        packages=find_packages(os.path.dirname(__file__) or '.'),
        install_requires=[
            '--allow-external pyPdf',
            '--allow-unverified pyPdf',
            'pyPdf',
            'Django == 1.7.2',
            'django-reversion == 1.8.5'
            'python-dateutil >= 2.2, < 2.3',
            'django-model-utils == 1.4.0',
            'django-ajax-selects == 1.3.5',
            'django-widget-tweaks < 1.2.0',
            'django-tastypie == 0.12.1',
            'interval == 1.0.0',
            'python-ldap',
            'reportlab >= 2.1, < 3.0',
            'xhtml2pdf',
            'https://codeload.github.com/ZTH1970/python-entrouvert/zip/master',
            'django-localflavor',
            'raven >= 3.5.2, < 3.6',
            'M2Crypto',
            '--allow-external pycairo',
            'django_select2 < 4.3',
            'django-journal'
            'south',
        ],
        dependency_links = [
            'http://django-swingtime.googlecode.com/files/django-swingtime-0.2.1.tar.gz#egg=django-swingtime-0.2.1',
        ],
)
