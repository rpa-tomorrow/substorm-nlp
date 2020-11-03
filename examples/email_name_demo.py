import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error
from lib.nlp import nlp
from lib.settings import load_settings

load_settings()
n = nlp.NLP("en_rpa_simple")

# Enable the SMTP server before running the following
try:
    text = "send email to John saying Hello there"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
