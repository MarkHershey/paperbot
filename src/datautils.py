# built-in modules
from pathlib import Path
from typing import Dict, List, Tuple

import firebase_admin

# external modules
import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore
from markkk.logger import logger
from markkk.time import timestamp_seconds

# local
from constants import *
from paper_class import Paper

# get papers directory
papers_dir = project_root / "papers"
assert papers_dir.is_dir()


class TelegramUser:
    def __init__(self, username: str, first_name: str = "", last_name: str = ""):
        self.username: str = username
        self.first_name: str = first_name
        self.last_name: str = last_name


###########################################################
def download_pdf(paper: Paper, save_dir=papers_dir) -> Path:
    save_dir = Path(save_dir)
    assert save_dir.is_dir()

    filepath = save_dir / f"{paper.paper_id}.pdf"
    if filepath.is_file():
        logger.warning(f"Paper PDF already exist at: {filepath}")
        return filepath
    else:
        try:
            response = requests.get(paper.pdf_url)
            with filepath.open(mode="wb") as f:
                f.write(response.content)
            return filepath
        except Exception as e:
            logger.error(e)
            return False


def save_paper_to_db(paper: Paper, force_overwrite=False):
    db_ref = db.collection(ALL_PAPER_PARENT).document(paper.paper_id)
    doc = db_ref.get()
    if doc.exists and not force_overwrite:
        return False
    else:
        db_ref.set(paper.to_dict())
        return True


def get_paper_from_db(paper_id: str) -> Paper:
    db_ref = db.collection(ALL_PAPER_PARENT).document(paper_id)
    doc = db_ref.get()
    if doc.exists:
        paper = Paper.from_dict(doc.to_dict())
        return paper
    else:
        return False


def create_new_user_db(user: TelegramUser):
    db_ref = db.collection(ALL_USER_PARENT).document(user.username)
    doc = db_ref.get()
    if doc.exists:
        logger.error("User already exists")
        return False
    else:
        profile = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_createdAt": timestamp_seconds(),
            "papers": {},
        }
        db_ref.set(profile)
        return True


def add_paper_to_user(paper: Paper, user: TelegramUser):
    db_ref = db.collection(ALL_USER_PARENT).document(user.username)
    doc = db_ref.get()
    if doc.exists:
        pass
    else:
        create_new_user_db(user)
        doc = db_ref.get()

    profile = doc.to_dict()
    userPapers: dict = profile.get("papers")
    if paper.paper_id not in userPapers:
        userPapers[paper.paper_id] = {
            "paper_id": paper.paper_id,
            "added_at": timestamp_seconds(),
            "labels": [],
            "notes": [],
        }
        profile["papers"] = userPapers
        db_ref.update(profile)
        return True
    else:
        logger.warning("paper already added in the past")
        return False


if __name__ == "__main__":

    pass
