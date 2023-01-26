"""Main window for GUI."""
# TODO: Config and enable internationalization.
import threading
from gettext import gettext as _
from pathlib import Path
from typing import Optional
from typing import Sequence
from webbrowser import open as open_url

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from . import help_dialogs
from . import preferences
from .. import default_files
from .. import whisper_process
from ..__about__ import APP_NAME_LOCALIZABLE
from ..__about__ import BUG_REPORT_URL
from ..__about__ import PROJECT_HOME_PAGE_URL
from ..config import Config
from ..whisper import whisper


class MainWindow(QtWidgets.QMainWindow):
    """Main window."""

    def __init__(self) -> None:
        """Config window and initialize base components."""
        super().__init__()

        self.resize(900, 450)
        self.setWindowTitle(APP_NAME_LOCALIZABLE)

        main_panel = MainPanel()

        self.setCentralWidget(main_panel)

        self.menu_bar = self.menuBar()

        config_menu = self.menu_bar.addMenu(_("&Config"))

        preferences_action = QtGui.QAction(
            QtGui.QIcon().fromTheme("settings"), _("&Preferences"), self
        )
        preferences_action.triggered.connect(
            lambda: preferences.PreferencesDialog().exec()
        )
        config_menu.addAction(preferences_action)

        save_current_options = QtGui.QAction(
            QtGui.QIcon().fromTheme("document-save"),
            _("&Sava Current Options as Default"),
            self,
        )
        # TODO: Implement save current options action.
        # save_current_options.triggered.connect()
        config_menu.addAction(save_current_options)

        # Action to exit the application.
        exit_app = QtGui.QAction(
            QtGui.QIcon().fromTheme("application-exit"), _("E&xit Application"), self
        )
        exit_app.setShortcut("Ctrl+Q")
        exit_app.triggered.connect(QtWidgets.QApplication.instance().quit)
        config_menu.addAction(exit_app)

        help_menu = self.menu_bar.addMenu(_("&Help"))

        github_page = QtGui.QAction(
            QtGui.QIcon.fromTheme("github-repo"), _("&GitHub"), self
        )
        github_page.triggered.connect(lambda: open_url(PROJECT_HOME_PAGE_URL))
        help_menu.addAction(github_page)

        report_bug = QtGui.QAction(
            QtGui.QIcon.fromTheme("tools-report-bug"), _("Report a &Bug"), self
        )
        report_bug.triggered.connect(lambda: open_url(BUG_REPORT_URL))
        help_menu.addAction(report_bug)

        about = QtGui.QAction(
            QtGui.QIcon.fromTheme("help-about-symbolic"), _("&About"), self
        )
        about.triggered.connect(lambda: help_dialogs.About().exec())
        help_menu.addAction(about)


class MainPanel(QtWidgets.QWidget):
    """Central widget for the main window."""

    reset_gui_after_sucess = QtCore.Signal()
    reset_gui_after_cancel = QtCore.Signal()
    lock_buttons_during_operation = QtCore.Signal()
    update_progress = QtCore.Signal(str, int)
    update_file_progress = QtCore.Signal(str)
    set_progress_indefinite = QtCore.Signal()
    show_message = QtCore.Signal(str, str, Optional[str])
    toggle_generate_cancel_button = QtCore.Signal()

    # To tell the processes thread that the task was canceled and didn't success.
    processes_thread_stop = threading.Event()

    def __init__(self) -> None:
        """Initialize base components."""
        super().__init__()

        # Load config
        self.__config = Config()
        self.__config.read_config()
        # TODO: Set GUI options with the loaded config.

        # Accept drap files to the panel.
        # Configured in self.dragEnterEvent, self.dragMoveEvent, self.dropEvent.
        self.setAcceptDrops(True)

        main_layout = QtWidgets.QVBoxLayout(self)

        # Where you can select files, remove files and view them is a list.
        upper_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(upper_layout)

        # Where the select and remove buttons are located.
        files_controls_layout = QtWidgets.QVBoxLayout()
        files_controls_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        upper_layout.addLayout(files_controls_layout)

        # The Select File(s) button.
        self.__b_select_files = QtWidgets.QPushButton(_("&Select File(s)"))
        self.__b_select_files.setFixedSize(150, 35)
        files_controls_layout.addWidget(self.__b_select_files)
        self.__b_select_files.clicked.connect(self.__listener_selecting_files)

        # The Remove File(s) button.
        self.__b_remove_files = QtWidgets.QPushButton(_("&Remove File(s)"))
        self.__b_remove_files.setFixedSize(150, 35)
        self.__b_remove_files.setDisabled(True)
        files_controls_layout.addWidget(self.__b_remove_files)
        self.__b_remove_files.clicked.connect(self.__listener_removing_files)

        # Where the files list and it's description are located.
        files_list_layout = QtWidgets.QVBoxLayout()
        upper_layout.addLayout(files_list_layout)

        # The files list description.
        files_list_layout.addWidget(
            QtWidgets.QLabel(
                _("List of files to generate transcribe audio / generate subtitles")
            )
        )

        # The files list.
        self.__selected_files_list = QtWidgets.QListWidget()
        self.__selected_files_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        files_list_layout.addWidget(self.__selected_files_list)

        # A spacer
        main_layout.addItem(QtWidgets.QSpacerItem(0, 10))

        # Where you can select an output directory
        output_directory_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(output_directory_layout)

        self.__b_select_output = QtWidgets.QPushButton(_("Output Directory"))
        self.__b_select_output.setFixedSize(150, 35)
        output_directory_layout.addWidget(self.__b_select_output)
        self.__b_select_output.clicked.connect(
            self.__listener_selecting_output_directory
        )

        self.__output_directory = QtWidgets.QLineEdit()
        self.__output_directory.setReadOnly(True)
        self.__output_directory.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        # TODO: Implement a click action.
        self.__output_directory.setToolTip(_("Click to open directory"))
        output_directory_layout.addWidget(self.__output_directory)
        # Default output directory.
        self.__output_directory.setText(str(Path.home()))

        # A spacer
        main_layout.addItem(QtWidgets.QSpacerItem(0, 15))

        # Where you can select main wisper options.
        options_layout = QtWidgets.QHBoxLayout()
        options_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addLayout(options_layout)

        # Select model
        options_layout.addWidget(QtWidgets.QLabel(_("Model")))

        self.__cobx_model = QtWidgets.QComboBox()
        self.__cobx_model.addItems(whisper.available_models())
        self.__cobx_model.setMaximumWidth(self.__cobx_model.minimumSizeHint().width())
        options_layout.addWidget(self.__cobx_model)

        options_layout.addSpacing(35)

        # Select language
        options_layout.addWidget(QtWidgets.QLabel(_("Audio Language")))

        self.__cobx_audio_lang = QtWidgets.QComboBox()
        self.__cobx_audio_lang.addItem("Auto")
        self.__cobx_audio_lang.addItems(
            (x.title() for x in whisper.tokenizer.LANGUAGES.values())
        )
        self.__cobx_audio_lang.setMaximumWidth(
            self.__cobx_audio_lang.minimumSizeHint().width()
        )
        options_layout.addWidget(self.__cobx_audio_lang)

        options_layout.addSpacing(35)

        # Select task
        options_layout.addWidget(QtWidgets.QLabel(_("Task")))

        self.__cobx_task = QtWidgets.QComboBox()
        self.__cobx_task.addItems((_("Transcribe"), _("Translate")))  # Index 0, 1
        self.__cobx_task.setMaximumWidth(self.__cobx_task.minimumSizeHint().width())
        options_layout.addWidget(self.__cobx_task)

        options_layout.addSpacing(35)

        # Select device
        options_layout.addWidget(QtWidgets.QLabel(_("Device")))

        self.__cobx_device = QtWidgets.QComboBox()
        self.__cobx_device.addItems(("CUDA", "CPU"))
        self.__cobx_device.setMaximumWidth(self.__cobx_device.minimumSizeHint().width())
        options_layout.addWidget(self.__cobx_device)

        options_layout.addSpacing(35)

        # Set threads
        options_layout.addWidget(QtWidgets.QLabel(_("Threads")))

        self.__sp_threads = QtWidgets.QSpinBox()
        self.__sp_threads.setMaximumWidth(self.__sp_threads.minimumSizeHint().width())
        options_layout.addWidget(self.__sp_threads)

        options_layout.addSpacing(35)

        # Where you can select advanced wisper options.
        # TODO: Hide advanced options inside a fold.
        advanced_options_layout = QtWidgets.QHBoxLayout()
        advanced_options_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addLayout(advanced_options_layout)

        # Set temperature
        advanced_options_layout.addWidget(QtWidgets.QLabel(_("Temperature")))

        # TODO: Find a way to apply tuple rather then just single float.
        self.__sp_temperature = QtWidgets.QDoubleSpinBox()
        self.__sp_temperature.setValue(0)
        self.__sp_temperature.setMaximumWidth(
            self.__sp_temperature.minimumSizeHint().width()
        )
        advanced_options_layout.addWidget(self.__sp_temperature)

        advanced_options_layout.addSpacing(35)

        # Set best_of
        advanced_options_layout.addWidget(QtWidgets.QLabel(_("Best of")))

        self.__sp_best_of = QtWidgets.QSpinBox()
        self.__sp_best_of.setValue(5)
        self.__sp_best_of.setMaximumWidth(self.__sp_best_of.minimumSizeHint().width())
        advanced_options_layout.addWidget(self.__sp_best_of)

        advanced_options_layout.addSpacing(35)

        # Set beam_size
        advanced_options_layout.addWidget(QtWidgets.QLabel(_("Beam Size")))

        self.__sp_beam_size = QtWidgets.QSpinBox()
        self.__sp_beam_size.setValue(5)
        self.__sp_beam_size.setMaximumWidth(
            self.__sp_beam_size.minimumSizeHint().width()
        )
        advanced_options_layout.addWidget(self.__sp_beam_size)

        advanced_options_layout.addSpacing(35)

        # Set fp16
        advanced_options_layout.addWidget(QtWidgets.QLabel(_("fp16")))

        self.__cbx_fp16 = QtWidgets.QCheckBox()
        self.__cbx_fp16.setMaximumWidth(self.__cbx_fp16.minimumSizeHint().width())
        advanced_options_layout.addWidget(self.__cbx_fp16)

        # TODO: Add patience option.
        # TODO: Add length_penalty option.
        # TODO: Add suppress_tokens option.
        # TODO: Add initial_prompt option.
        # TODO: Add condition_on_previous_text option.
        # TODO: Add temperature_increment_on_fallback option. See how it works in transcribe.cli
        # TODO: Add compression_ratio_threshold option.
        # TODO: Add logprob_threshold option.
        # TODO: Add no_speech_threshold option.

        # A spacer
        main_layout.addItem(QtWidgets.QSpacerItem(0, 20))

        # A button to run the generator
        self.__b_run_generator = QtWidgets.QPushButton(
            _("Transcribe Audio / Generate Subtitles")
        )
        self.__b_run_generator.setFixedHeight(35)
        self.__b_run_generator.setDisabled(True)
        main_layout.addWidget(self.__b_run_generator, alignment=QtCore.Qt.AlignCenter)
        self.__b_run_generator.clicked.connect(self.__listener_running_generator)

        self.__b_cancel_generator = QtWidgets.QPushButton(_("Cancel Operation"))
        self.__b_cancel_generator.setFixedHeight(35)
        self.__b_cancel_generator.hide()
        main_layout.addWidget(
            self.__b_cancel_generator, alignment=QtCore.Qt.AlignCenter
        )
        self.__b_cancel_generator.clicked.connect(self.__listener_cancel_generator)

        # A spacer
        main_layout.addItem(QtWidgets.QSpacerItem(0, 20))

        # A progress bar
        self.__progress_bar = QtWidgets.QProgressBar()
        self.__progress_bar.setValue(0)
        main_layout.addWidget(self.__progress_bar)

        progress_bar_description_layout = QtWidgets.QHBoxLayout()
        progress_bar_description_layout.setAlignment(QtCore.Qt.AlignLeft)
        main_layout.addLayout(progress_bar_description_layout)

        self.__current_file_progress_lable = QtWidgets.QLabel()
        progress_bar_description_layout.addWidget(self.__current_file_progress_lable)
        self.__current_operation_progress_lable = QtWidgets.QLabel()
        progress_bar_description_layout.addWidget(
            self.__current_operation_progress_lable
        )

        # Connect signals to functions
        self.reset_gui_after_sucess.connect(self.__listener_reseting_gui_after_success)
        self.reset_gui_after_cancel.connect(self.__listener_reseting_gui_after_cancel)
        self.lock_buttons_during_operation.connect(
            self.__listener_locking_buttons_during_operation
        )
        self.update_progress.connect(self.__listener_updateing_progress)
        self.update_file_progress.connect(self.__listener_updating_file_progress)
        self.set_progress_indefinite.connect(
            self.__listener_setting_progress_indefinite
        )
        self.show_message.connect(self.__listener_show_message)
        self.toggle_generate_cancel_button.connect(
            self.__listener_toggle_generate_cancel_button
        )

    def __add_files_to_list(self, files: tuple[str, ...]) -> None:
        """
        Add files to the files list.

        Filter not video nor audio files, and files that has been selected before.
        """
        current_files_list = tuple(
            self.__selected_files_list.item(i).text()
            for i in range(self.__selected_files_list.count())
        )

        # TODO: Filter files if they has a not video nor audio mime type.

        for file in files:
            if file not in current_files_list:
                self.__selected_files_list.addItem(file)

        # Enable those buttons only if list of files is not empty.
        # No problem if selected files were duplicates, since the list is not empty.
        self.__b_run_generator.setEnabled(True)
        self.__b_remove_files.setEnabled(True)

    def __listener_selecting_files(self) -> None:
        """Get files list from QFileDialog, then add them to the list."""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            caption="Select media",
            # TODO: Improve the filter by adding more mime types.
            filter="All Media Files (*.mp3 *.mp4 *.wav *.m4a *.wma)",
        )

        if files:
            self.__add_files_to_list(tuple(files))

    def __listener_removing_files(self) -> None:
        """Get selected files then delete them and disable buttons if list is empty."""
        for item in self.__selected_files_list.selectedItems():
            self.__selected_files_list.takeItem(self.__selected_files_list.row(item))

        if self.__selected_files_list.count() == 0:
            # If no items left disables those buttons
            self.__b_remove_files.setEnabled(False)
            self.__b_run_generator.setEnabled(False)

    def __listener_selecting_output_directory(self) -> None:
        """Get an output directory from the user and display it."""
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, caption="Select output directory", dir=self.__output_directory.text()
        )

        if selected_directory:
            self.__output_directory.setText(selected_directory)

    # TODO:
    # def __listener_opening_output_directory(self) -> None:
    #         open_file(self.__output_directory.text())

    def __listener_reseting_gui_after_success(self) -> None:
        """Clear list and enable buttons after success."""
        self.__selected_files_list.clear()

        self.__b_run_generator.setEnabled(False)
        self.__b_remove_files.setEnabled(False)

        self.__listener_reseting_gui_after_cancel()

    def __listener_reseting_gui_after_cancel(self) -> None:
        """Reset progress bar and enable buttons after canceling the operation."""
        # Show generate button insted of cancel button.
        self.__listener_toggle_generate_cancel_button()

        self.__reset_progressbar()

        if self.__b_run_generator.isEnabled():
            self.__b_remove_files.setEnabled(True)

        self.__b_select_files.setEnabled(True)
        self.__b_select_output.setEnabled(True)
        self.__cobx_model.setEnabled(True)
        self.__cobx_audio_lang.setEnabled(True)
        self.__cobx_task.setEnabled(True)
        self.__cobx_device.setEnabled(True)
        self.__sp_threads.setEnabled(True)
        self.__sp_temperature.setEnabled(True)
        self.__sp_best_of.setEnabled(True)
        self.__sp_beam_size.setEnabled(True)
        self.__cbx_fp16.setEnabled(True)

    def __listener_locking_buttons_during_operation(self) -> None:
        """Disable buttons when there is a running operation."""
        self.__b_remove_files.setEnabled(False)
        self.__b_select_files.setEnabled(False)
        self.__b_select_output.setEnabled(False)
        self.__cobx_model.setEnabled(False)
        self.__cobx_audio_lang.setEnabled(False)
        self.__cobx_task.setEnabled(False)
        self.__cobx_device.setEnabled(False)
        self.__sp_threads.setEnabled(False)
        self.__sp_temperature.setEnabled(False)
        self.__sp_best_of.setEnabled(False)
        self.__sp_beam_size.setEnabled(False)
        self.__cbx_fp16.setEnabled(False)

    def __listener_updateing_progress(self, string: str, percentage: int) -> None:
        """When there is a progress update display it in the GUI."""
        self.__current_operation_progress_lable.setText(string)
        self.__progress_bar.setValue(percentage)

    def __listener_updating_file_progress(self, string: str) -> None:
        """Update the GUI to display which file it currently being processed."""
        self.__current_file_progress_lable.setText(string)

    def __listener_setting_progress_indefinite(self) -> None:
        """Make the progress bar indefinite by making no minimum or maximum value."""
        self.__progress_bar.setMinimum(0)
        self.__progress_bar.setMaximum(0)

    def __reset_progressbar(self) -> None:
        """Reset the progress bar to its default status."""
        self.__progress_bar.setMinimum(0)
        self.__progress_bar.setMaximum(100)
        self.__listener_updateing_progress("", 0)

    def __listener_show_message(
        self, message_type: str, text: str, title: Optional[str] = None
    ) -> int:
        """Show messages as a message box widget in the GUI."""
        if message_type == "info":
            message = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, title, text
            )
        elif message_type == "error":
            message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, title, text)
        else:
            raise TypeError(f'No message type called "{message_type}" is available.')

        return message.exec()

    def __listener_toggle_generate_cancel_button(self) -> None:
        """Show a `generate` button when the task is not running, and vice versa."""
        if self.__b_run_generator.isHidden():
            self.__b_run_generator.setHidden(False)
            self.__b_cancel_generator.setHidden(True)
        else:
            self.__b_run_generator.setHidden(True)
            self.__b_cancel_generator.setHidden(False)

    def __listener_running_generator(self) -> None:
        """Actions when the task is started."""
        self.lock_buttons_during_operation.emit()

        # Show cancel button insted of generate button.
        self.toggle_generate_cancel_button.emit()

        self.processes = [
            whisper_process.WhisperProcess(
                audio_file,
                self.__config.get_option("prefrences", "model_directory")
                or str(default_files.xdg_cache_dir()),
                self.__cobx_audio_lang.currentText(),
                self.__output_directory.text(),
                self.__cobx_model.currentText(),
                self.__cobx_device.currentText().lower(),
                self.__sp_threads.value(),
                options={
                    "task": ("transcribe", "translate")[
                        self.__cobx_task.currentIndex()
                    ],
                    "temperature": self.__sp_temperature.value(),
                    "best_of": self.__sp_best_of.value(),
                    "beam_size": self.__sp_beam_size.value(),
                    "fp16": self.__cbx_fp16.isChecked(),
                },
            )
            for audio_file in tuple(
                self.__selected_files_list.item(i).text()
                for i in range(self.__selected_files_list.count())
            )
        ]

        def thread_run() -> None:
            """Run processes under a thread to detect when they finish without freezing the GUI."""
            for process in self.processes:
                # PERF: Set max processes count and don't run a lot of process at ones.
                process.start()

            # TODO: Optionaly run processes in queue.
            # self.update_file_progress.emit(process.audio_file_path)

            for process in self.processes:
                process.join()

            if not self.processes_thread_stop.isSet():
                self.reset_gui_after_sucess.emit()
            self.processes_thread_stop.clear()

        self.thread = threading.Thread(target=thread_run)
        self.thread.start()

        # TODO: Display progress bar.
        # self.update_progress.emit()

        # TODO: Display errors and warnings.
        # self.__show_message()

    def __listener_cancel_generator(self) -> None:
        """Actions when the task is canceled."""
        self.update_progress.emit(_("Cancelling..."), 0)
        self.update_file_progress.emit("")

        self.processes_thread_stop.set()

        for process in self.processes:
            try:
                process.terminate()
            except AttributeError:
                # When process hasn't started yet or already finished.
                pass

        self.set_progress_indefinite.emit()
        self.reset_gui_after_cancel.emit()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:  # noqa: N802
        """When a drag action enters the panel."""
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:  # noqa: N802
        """While a drag action is in progress."""
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:  # noqa: N802
        """When a drag action is completed."""
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            self.__add_files_to_list(
                tuple(url.toLocalFile() for url in event.mimeData().urls())
            )
        else:
            event.ignore()


def ui_main(argv: Sequence[str]) -> int:
    """Start the GUI."""
    app = QtWidgets.QApplication(argv)
    window = MainWindow()
    window.show()
    return app.exec()
