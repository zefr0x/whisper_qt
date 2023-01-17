"""Preferences and settings widgets and dialogs."""
from gettext import gettext as _

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from ..__about__ import APP_NAME_LOCALIZABLE


class PreferencesDialog(QtWidgets.QDialog):
    """"""

    def __init__(self):
        """"""
        super().__init__()

        self.setWindowTitle(APP_NAME_LOCALIZABLE + _(" Preferences"))
