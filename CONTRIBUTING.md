# Contributing

## Bug report
For now [GitHub bug traker](https://github.com/zer0-x/whisper_qt/issues) is used for this project.

## Development
- The 3rd version of the [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) programming language is used mainly in this project.
- Dependencies managment is handled using [requirements files](requirements) with [pip-tools](https://pip-tools.rtfd.io/).
    - `requirements.in` contain requirements for running the application and `requirements-dev.in` contain requirements for development.
    - `.txt` files are locked requirements with hashes generated using `pip-tools` to provide a reproducible environment.
    - For development you will need to use both files, while users just need to use the `requirements.txt` file.

>    `pre-commit` will take care about generating `.txt` files. You should just edit `.in` files or use `pip-tools` to upgrade locked requirements.

### Create a virtual environment and install dependencies
First clone the git repository:
```
git clone https://github.com/zer0-x/whisper_qt.git
```

For development you are recomended to use [pip-tools](https://pip-tools.rtfd.io/) for reproducing the same environment.
1. Create a virtual environment and activate it
```shell
virtualenv .env

source .env/bin/activate
```
2. Install `pip-tools` in the virtualenv
```shell
pip install pip-tools
```
3. Run the folowing command in the project's root directory to install all the dependencies for development
```shell
pip-sync requirements/{requirements,requirements-dev}.txt
```
4. Then you can run the application as a python module
```shell
python3 -m whisper_qt
```

### Style
- You should [type hint](https://docs.python.org/3/library/typing.html) every thing as possible.
- You should comment every thing to keep the code easy to read. Every file, every class, every function and any line that need a comment.

#### Installing `pre-commit`
To make every thing easy [**`pre-commit`**](https://pre-commit.com/) is used in this project, it should run in every commit, so you shouldn't commit any thing without checking it first.

First install it:
```shell
pip install pre-commit
```

> You can use another way to install it, maybe from your OS's package manager.


Then add it as a git hook while you are inside the repository:
```shell
pre-commit install
```

## Testing
...

## Translation
The application's GUI is prepared for [internationalisation](https://en.wikipedia.org/wiki/Internationalization_and_localization), but I didn't set it up yet.

For now you have two files to translate:
- [`io.github.zer0_x.Whisper_Qt.desktop`](https://github.com/zer0-x/whisper_qt/blob/main/io.github.zer0_x.Whisper_Qt.desktop)
- [`io.github.zer0_x.Whisper_Qt.metainfo.xml`](https://github.com/zer0-x/whisper_qt/blob/main/io.github.zer0_x.Whisper_Qt.metainfo.xml)
