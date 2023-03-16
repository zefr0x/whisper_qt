> **Warning** : This repository/project is no longer maintained.

If you want an alternative, take a look at [Buzz](https://github.com/chidiwilliams/buzz).

---

<div align = center>

![Logo](assets/io.github.zer0_x.Whisper_Qt.svg)

<h1>Whisper Qt</h1>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/zer0-x/whisper_qt/main.svg)](https://results.pre-commit.ci/latest/github/zer0-x/whisper_qt/main)

<!-- TODO: Add descreption. -->

---

[<kbd><br><b>Install</b><br><br></kbd>](#installation)
<!-- [<kbd><br><b>Screenshots</b><br><br></kbd>](#screenshots) -->
[<kbd><br><b>Contribute</b><br><br></kbd>](CONTRIBUTING.md)
[<kbd><br><b>Packaging</b><br><br></kbd>](PACKAGING.md)

---

<br>

</div>

## Features
- 🧾 Free software under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html) licence.
- ...

# Screenshots

<img src = "https://user-images.githubusercontent.com/65136727/225508467-4d1efa69-76ec-4cc4-9f6b-182db8db502d.png" height="300px">

<sub>The theme might be differant depending on your desktop environment.</sub>

## Installation
### Flatpak
Not available yet...
### AppImage
Not available yet...
### AUR
Not available yet...
### From the git repo <sup>`(Not recomended)`</sup>
1. Clone the repository with it's submodules from github, then `cd` to it
```shell
git clone --recurse-submodules https://github.com/zer0-x/whisper_qt.git
cd whisper_qt
```
2. Use the `setup.py` file to install it
```shell
python3 setup.py install
```
> You can create a virtual environment before that if you wanted.
3. Now it should be in your path. Just type `whisper-qt` to run the GUI
```shell
whisper-qt
```

## Troubleshooting
- The application is using Qt6 so it might not be theamed as your system, since it is not supported by a lot of themes. There is no sulotion other then wating for the support.
