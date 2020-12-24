from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


################## FIREBASE ################################################
# Use a service account
_cred = credentials.Certificate(
    "src/data/paperbot-31c08-firebase-adminsdk-gznc7-a2c6188cbc.json"
)
firebase_admin.initialize_app(_cred)

db = firestore.client()

ALL_PAPER_PARENT = "papers"
ALL_USER_PARENT = "users"
############################################################################


# get project root and papers directory
project_root: Path = Path(__file__).resolve().parent.parent