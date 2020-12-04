import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from markkk.logger import logger

from paper_getter import Paper

# Use a service account
cred = credentials.Certificate(
    "src/data/paperbot-31c08-firebase-adminsdk-gznc7-a2c6188cbc.json"
)
firebase_admin.initialize_app(cred)

db = firestore.client()

ALL_PAPER_PARENT = "papers"
ALL_USER_PARENT = "users"


def save_paper(paper: Paper, force_overwrite=False):
    db_ref = db.collection(ALL_PAPER_PARENT).document(paper.paper_id)
    doc = db_ref.get()
    if doc.exists and not force_overwrite:
        return False
    else:
        db_ref.set(paper.to_dict())
        return True


def get_paper_db(paper_id: str) -> Paper:
    db_ref = db.collection(ALL_PAPER_PARENT).document(paper_id)
    doc = db_ref.get()
    if doc.exists:
        paper = Paper.from_dict(doc.to_dict())
        return paper
    else:
        return False


def save_record(record):
    # TODO
    pass


def get_list_of_paper_for_user(user):
    # TODO
    pass
