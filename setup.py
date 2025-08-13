from pathlib import Path
import re
import setuptools

setup_dir = Path(__file__).resolve().parent

version = re.search( r'VERSION = "(.*)"', Path(setup_dir, 'calcuresu/consts.py').open().read())
if version is None:
    raise SystemExit("Could not determine version to use")
version = version.group(1)

setuptools.setup(
    name='calcuresu',
    author='Guy Sudai',
    author_email='sudaiguy1@gmail.com',
    url='https://github.com/guysudai1/calcuresu',
    description='Modern TUI task manager (re-written by guysu)',
    long_description=Path(setup_dir, 'README.md').open().read(),
    long_description_content_type='text/markdown',
    license='MIT',
    entry_points={
        "console_scripts": [
            "calcuresu = calcuresu.__main__:cli"
        ]
    },
    install_requires=["prompt_toolkit", "flufl.lock"],
    version=version,
    python_requires='~=3.10',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Utilities",
    ],
    packages=["calcuresu", "calcuresu.translations", "calcuresu.views", "calcuresu.views.screens", "calcuresu.views.fragments", "calcuresu.classes"],
    include_package_data=True,
)
