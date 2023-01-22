"""Processes to run whisper in them."""
import multiprocessing
from os import environ
from pathlib import Path

from .__about__ import APP_NAME
from .whisper import whisper


class WhisperProcess(multiprocessing.Process):
    """Process to run whisper in it."""

    def __init__(
        self,
        audio_file_path: str,
        audio_language: str,
        output_directory: str,
        model: str,
        device: str,
        threads: int,
        options: dict,
    ) -> None:
        """Get arguments from the main process."""
        super().__init__()

        self.audio_file_path = audio_file_path
        self.output_directory = output_directory
        self.model = model
        self.device = device
        self.threads = threads
        self.options = options

        if audio_language == "Auto":
            self.audio_language = None
        else:
            self.audio_language = audio_language

        # TODO: Add prefrece option to select a model_dir.

        # Use the XDG base directory.
        if environ.get("XDG_CACHE_HOME"):
            # The (or "") is to pass the type check.
            xdg_cache_home = Path(environ.get("XDG_CACHE_HOME") or "")
        else:
            xdg_cache_home = Path.home().joinpath(".cache")

        self.model_dir = str(xdg_cache_home / APP_NAME)

    def run(self) -> None:
        """Run when the process starts."""
        if self.threads > 0:
            whisper.torch.set_num_threads(self.threads)

        # TODO: If model is not downloaded, warn user that it will take time.
        # TODO: If an english only module was used in other language warn user.
        # TODO: If a non-english language was used in english warn user.
        model = whisper.load_model(self.model, self.device, self.model_dir)

        result = model.transcribe(
            self.audio_file_path,
            verbose=True,
            language=self.audio_language,
            **self.options
        )

        # Save to .srt file
        with open(
            Path(self.output_directory) / (Path(self.audio_file_path).name + ".srt"),
            "w",
        ) as file:
            whisper.utils.write_srt(result["segments"], file)
