"""
The commands available in the CLI
"""

import sys
import os
from config import config_model_language, choose_model_version

sys.path.append(".")

from lib.nlp.model_installer import Model_Installer  # noqa: E402
from lib.settings import SETTINGS, get_model_languages, update_settings, get_model_versions


def commands(arr, nlp):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    elif arr[0] == "language" or arr[0] == "lang":
        SETTINGS["user"]["language"] = config_model_language(get_model_languages())
        SETTINGS["user"]["model_version"] = choose_model_version(get_model_versions(SETTINGS["user"]["language"]))
        update_settings("../config/user", SETTINGS["user"])
    elif arr[0] == "install" or arr[0] == "i":
        model_installer = Model_Installer()
        language = config_model_language(model_installer.get_languages())
        version = choose_model_version(model_installer.get_versions(language))
        model_installer.install(language, version)
    else:
        listToStr = " ".join(map(str, arr))
        try:
            response = nlp.run(listToStr)
            print(response + "\n")
        except Exception as e:
            print("Failed to execute action.\n", e, file=sys.stderr)


def prompt():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())
