import sys
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.build_scripts import build_scripts

__version__ = '0.1'

setup(name='mytest',
      url='http://example.com/',
      author='Markiyan',
      author_email='markiyan.kushnir@gmail.com',
      description='My test task',
      version=__version__,
      package_dir={'mytest': 'src/mytest'},
      #package_data={'mytest': ['templates/*', 'static/*']},
      packages=['mytest',
      ],
      data_files = [
          ('etc/mytest', ['src/mytest.conf']),
      ],
     )

