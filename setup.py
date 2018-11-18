from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='sql2csv',
    version='1.1',
    description='Run MySQL and PostgreSQL queries and store result in CSV',
    long_description=long_description,
    author='Gabriel Bordeaux',
    author_email='pypi@gab.lc',
    url='https://github.com/gabfl/sql2csv',
    license='MIT',
    packages=['sql2csv'],
    package_dir={'sql2csv': 'src'},
    install_requires=['argparse', 'PyYAML', 'pymysql',
                      'psycopg2-binary'],  # external dependencies
    entry_points={
        'console_scripts': [
            'sql2csv = sql2csv.sql2csv:main',
        ],
    },
    classifiers=[  # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        #  'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        #  'Development Status :: 5 - Production/Stable',
    ],
)
