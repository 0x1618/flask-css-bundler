from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '1.0'
DESCRIPTION = 'Easy Flask CSS bundler'
LONG_DESCRIPTION = 'A package that allows you to combine CSS files and then generate a bundle with the used only.'

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# Setting up
setup(
    name="flask_css_bundler",
    version=VERSION,
    author="0x1618 aka ctrlshifti (Maksymilian Sawicz)",
    author_email="<max.sawicz@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description='Github page: https://github.com/0x1618/CSS-Selector-Minifier \n' + long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'css', 'html', 'js', 'minify', 'css selectors', 'selector', 'selectors', 'minify css selectors']
)