from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

__all__ = ["db", "ALL_PAPER_PARENT", "ALL_USER_PARENT", "project_root"]


################## FIREBASE ################################################
# Use a service account
_cred = credentials.Certificate(
    "src/data/paperbot-31c08-firebase-adminsdk-gznc7-5b4edd1da0.json"
)
firebase_admin.initialize_app(_cred)

db = firestore.client()

ALL_PAPER_PARENT = "papers"
ALL_USER_PARENT = "users"
############################################################################


# get project root
project_root: Path = Path(__file__).resolve().parent.parent
