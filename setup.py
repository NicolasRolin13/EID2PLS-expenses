
from setuptools import find_packages, setup


setup(
    name='expenses',
    version='0.1',
    description=('Does pretty much nothing'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    packages=find_packages(),
    entry_points={'console_scripts': [
        'mon_entry_point = expenses.core:does_nothing',
    ]},
)