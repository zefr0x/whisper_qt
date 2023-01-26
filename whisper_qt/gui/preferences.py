"""Preferences and settings widgets and dialogs."""
from gettext import gettext as _

from PySide6 import QtCore
from PySide6 import QtWidgets

from .. import default_files
from ..__about__ import APP_NAME_LOCALIZABLE
from ..config import Config


class PreferencesDialog(QtWidgets.QDialog):
    """Application preferences dialog."""

    def __init__(self) -> None:
        """Initilize main componant of the dialog."""
        super().__init__()

        self.setWindowTitle(APP_NAME_LOCALIZABLE + _(" Preferences"))

        self.resize(400, 200)

        self.__config = Config()
        self.__config.read_config()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Where you can select a model directory
        main_layout.addWidget(
            QtWidgets.QLabel(_("<h2>Whisper</h2>")),
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter
            | QtCore.Qt.AlignmentFlag.AlignTop,
        )
        model_directory_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(model_directory_layout)

        self.__b_select_model_dir = QtWidgets.QPushButton(_("Module Directory"))
        self.__b_select_model_dir.setFixedSize(150, 35)
        model_directory_layout.addWidget(self.__b_select_model_dir)
        self.__b_select_model_dir.clicked.connect(
            self.__listener_selecting_model_directory
        )

        # Search for value in config file, if no then use the home directory as default.
        self.__model_directory = QtWidgets.QLineEdit(
            self.__config.get_option("preferences", "model_directory")
            or str(default_files.xdg_cache_dir())
        )
        self.__model_directory.setReadOnly(True)
        self.__model_directory.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.__model_directory.setMinimumWidth(
            self.__model_directory.sizeHint().width()
        )
        # TODO: Implement a click action.
        self.__model_directory.setToolTip(_("Click to open directory"))
        model_directory_layout.addWidget(self.__model_directory)

        main_layout.addStretch()

        # Dialog footer
        footer = QtWidgets.QHBoxLayout()
        footer.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom
        )
        main_layout.addLayout(footer)

        self.__b_apply_changes = QtWidgets.QPushButton(_("Apply"))
        footer.addWidget(self.__b_apply_changes)
        self.__b_apply_changes.clicked.connect(self.__listener_apply_changes)

        self.__b_close = QtWidgets.QPushButton(_("Close"))
        footer.addWidget(self.__b_close)
        self.__b_close.clicked.connect(self.close)

        # TODO: Add button to reset preferences.

    def __listener_selecting_model_directory(self) -> None:
        """Get a model directory from the user and display it."""
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, caption="Select model directory", dir=self.__model_directory.text()
        )

        if selected_directory:
            self.__model_directory.setText(selected_directory)
            self.__config.set_option(
                "preferences", "model_directory", selected_directory
            )

    def __listener_apply_changes(self) -> None:
        """Save proferences to config file."""
        self.__config.write_config()
