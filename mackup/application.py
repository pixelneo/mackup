"""
Application Profile.

An Application Profile contains all the information about an application in
Mackup. Name, files, ...
"""
import os

from .mackup import Mackup
from . import utils


class ApplicationProfile(object):

    """Instantiate this class with application specific data."""

    def __init__(self, mackup, files, dry_run, verbose):
        """
        Create an ApplicationProfile instance.

        Args:
            mackup (Mackup)
            files (list)
        """
        assert isinstance(mackup, Mackup)
        assert isinstance(files, set)

        self.mackup = mackup
        self.files = list(files)
        self.dry_run = dry_run
        self.verbose = verbose

    def getFilepaths(self, filename):
        """
        Get home and mackup filepaths for given file

        Args:
            filename (str)

        Returns:
            home_filepath, mackup_filepath (str, str)
        """
        return (
            os.path.join(os.environ["HOME"], filename),
            os.path.join(self.mackup.mackup_folder, filename),
        )

    def backup(self):
        """
        Backup the application config files.

        Algorithm:
            if exists home/file
              if home/file is a real file
                if exists mackup/file
                  are you sure ?
                  if sure
                    NO (rm mackup/file)
                    cp home/file mackup/file mv home/file mackup/file
                    NO link
                else
                  cp home/file mackup/file (NOT: mv home/file mackup/file)
                  NO link
        """
        # For each file used by the application
        for filename in self.files:
            (home_filepath, mackup_filepath) = self.getFilepaths(filename)

            # If the file exists 
            if os.path.isfile(home_filepath) or os.path.isdir(home_filepath):

                if self.verbose:
                    print(
                        "Backing up\n  {}\n  to\n  {} ...".format(
                            home_filepath, mackup_filepath
                        )
                    )
                else:
                    print("Backing up {} ...".format(filename))

                if self.dry_run:
                    continue

                # Check if we already have a backup
                if os.path.exists(mackup_filepath):

                    # Name it right
                    if os.path.isfile(mackup_filepath):
                        file_type = "file"
                    elif os.path.isdir(mackup_filepath):
                        file_type = "folder"
                    elif os.path.islink(mackup_filepath):
                        file_type = "link"
                    else:
                        raise ValueError("Unsupported file: {}".format(mackup_filepath))

                    # Ask the user if he really want to replace it
                    # if not utils.are_these_identical(home_filepath, mackup_filepath) and utils.confirm(
                    if utils.confirm(
                        "A {} named {} already exists in the"
                        " backup.\nAre you sure that you want to"
                        " replace it ?".format(file_type, mackup_filepath)
                    ):
                        # Delete the file in Mackup
                        utils.delete(mackup_filepath)
                        # Copy the file
                        utils.copy(home_filepath, mackup_filepath)
                else:
                    # Copy the file
                    utils.copy(home_filepath, mackup_filepath)
            elif self.verbose:
                if os.path.exists(home_filepath):
                    print(
                        "Doing nothing\n  {}\n  "
                        "is already backed up to\n  {}".format(
                            home_filepath, mackup_filepath
                        )
                    )
                elif os.path.islink(home_filepath):
                    print(
                        "Doing nothing\n  {}\n  "
                        "is a broken link, you might want to fix it.".format(
                            home_filepath
                        )
                    )
                else:
                    print("Doing nothing\n  {}\n  does not exist".format(home_filepath))

    def restore(self):
        """
        Restore the application config files.

        Algorithm:
            if exists mackup/file
              if exists home/file
                are you sure ?
                if sure
                  cp mackup/file home/file
              else
                cp mackup/file home/file
        """
        # For each file used by the application
        for filename in self.files:
            (home_filepath, mackup_filepath) = self.getFilepaths(filename)

            # If the file exists and is not already pointing to the mackup file
            # and the folder makes sense on the current platform (Don't sync
            # any subfolder of ~/Library on GNU/Linux)
            file_or_dir_exists = os.path.isfile(mackup_filepath) or os.path.isdir(
                mackup_filepath
            )
            supported = utils.can_file_be_synced_on_current_platform(filename)

            if file_or_dir_exists and supported:
                if self.verbose:
                    print(
                        "Restoring\n  linking {}\n  to      {} ...".format(
                            home_filepath, mackup_filepath
                        )
                    )
                else:
                    print("Restoring {} ...".format(filename))

                if self.dry_run:
                    continue

                # Check if there is already a file in the home folder
                if os.path.exists(home_filepath):
                    # Name it right
                    if os.path.isfile(home_filepath):
                        file_type = "file"
                    elif os.path.isdir(home_filepath):
                        file_type = "folder"
                    elif os.path.islink(home_filepath):
                        file_type = "link"
                    else:
                        raise ValueError("Unsupported file: {}".format(mackup_filepath))

                    if utils.confirm(
                        "You already have a {} named {} in your"
                        " home.\nDo you want to replace it with"
                        " your backup ?".format(file_type, filename)
                    ):
                        utils.copy(mackup_filepath, home_filepath)
                else:
                    utils.copy(mackup_filepath, home_filepath)
            elif self.verbose:
                if os.path.exists(home_filepath):
                    print(
                        "Doing nothing\n  {}\n  already linked by\n  {}".format(
                            mackup_filepath, home_filepath
                        )
                    )
                elif os.path.islink(home_filepath):
                    print(
                        "Doing nothing\n  {}\n  "
                        "is a broken link, you might want to fix it.".format(
                            home_filepath
                        )
                    )
                else:
                    print(
                        "Doing nothing\n  {}\n  does not exist".format(mackup_filepath)
                    )

    def uninstall(self):
        raise NotImplementedError('Uninstall is not implemented')
