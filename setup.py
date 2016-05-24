from setuptools import setup, find_packages

setup(
    name="tikzmagic",
    version="1.0.1",

    packages=find_packages(),
    install_requires=['IPython'],

    description='''
        A Jupyter extension for compiling and displaying images described by the TikZ language.
        ''',
    url='https://github.com/robjstan/tikzmagic',

    author='Rob J Stanley',
    author_email='rob@robjstanley.me.uk',

    license='MIT',
    classifiers=['Programming Language :: Python :: 3.5'],
)
