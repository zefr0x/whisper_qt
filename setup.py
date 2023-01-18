"""Setup file for the library."""
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

from whisper_qt.__about__ import __author__
from whisper_qt.__about__ import __description__
from whisper_qt.__about__ import __license__
from whisper_qt.__about__ import __maintainer__
from whisper_qt.__about__ import APP_VERSION


HERE = Path(__file__).parent

README = (HERE / "README.md").read_text()

URL = "https://github.com/zer0-x/whisper_qt"
ISSUES = "https://github.com/zer0-x/whisper_qt/issues"
CHANGELOG = "https://github.com/zer0-x/whisper_qt/blob/main/CHANGELOG.md"

setup(
    name="whisper_qt",
    version=APP_VERSION,
    author=__author__,
    maintainer=__maintainer__,
    license=__license__,
    description=__description__,
    long_description_content_type="text/markdown",
    long_description=README,
    url=URL,
    project_urls={
        "Issues": ISSUES,
        "Changelog": CHANGELOG,
    },
    packages=find_packages()
    + ["whisper_qt.whisper.whisper", "whisper_qt.whisper.whisper.normalizers"],
    entry_points={"console_scripts": ["whisper-qt = whisper_qt.__main__:main"]},
    # TODO: Add more keywords and classifiers.
    keywords=[
        "pyside6",
        "linux_desktop",
        "database-gui",
    ],
    classifiers=[
        "Environment :: X11 Applications :: Qt",
        "Environment :: X11 Applications :: KDE",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
