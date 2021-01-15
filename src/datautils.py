# built-in modules
from pathlib import Path
from typing import List, Dict, Tuple

# local
from helpers import timestamp_now
from constants import *

# external modules
import requests
from bs4 import BeautifulSoup
from markkk.logger import logger
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# get project root and papers directory
papers_dir = project_root / "papers"
assert papers_dir.is_dir()


class Paper:
    def __init__(
        self,
        paper_id="",
        title="",
        authors=[""],
        paper_url="",
        pdf_url="",
        code_url="",
        abstract="",
        comments="",
    ):
        self.paper_id: str = paper_id
        self.title: str = title
        self.authors: List[str] = authors
        self.paper_url: str = paper_url
        self.pdf_url: str = pdf_url
        self.code_url: str = code_url
        self.abstract: str = abstract
        self.comments: str = comments
        # derived
        self.first_author = self.authors[0]

    def __repr__(self) -> str:
        return self.title

    def to_dict(self) -> dict:
        _dict = {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "paper_url": self.paper_url,
            "pdf_url": self.pdf_url,
            "code_url": self.code_url,
            "abstract": self.abstract,
            "comments": self.comments,
        }
        return _dict

    @staticmethod
    def from_dict(src: dict):
        return Paper(
            paper_id=src.get("paper_id"),
            title=src.get("title"),
            authors=src.get("authors"),
            paper_url=src.get("paper_url"),
            pdf_url=src.get("pdf_url"),
            code_url=src.get("code_url"),
            abstract=src.get("abstract"),
            comments=src.get("comments"),
        )

    

########################################################### 


def process_url(url: str) -> Tuple[str]:

    def get_paper_id_from_url(url) -> str:
        while "/" in url:
            slash_idx = url.find("/")
            url = url[slash_idx + 1 :]

        if url.endswith(".pdf"):
            return url[:-4]
        else:
            return url

    # TODO: Validate URL

    if "arxiv.org/abs" in url:
        ## abstract page
        paper_id = get_paper_id_from_url(url)
        paper_url = url
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        return paper_id, paper_url, pdf_url
    elif "arxiv.org/pdf" in url:
        ## pdf page
        paper_id = get_paper_id_from_url(url)
        paper_url = f"https://arxiv.org/abs/{paper_id}"
        pdf_url = url
        return paper_id, paper_url, pdf_url
    else:
        logger.error("URL not supported")
        raise Exception("URL not supported")





def get_paper(url: str) -> Paper:
    try:
        paper_id, paper_url, pdf_url = process_url(url)
    except Exception as err:
        logger.error(err)
        raise Exception("URL not supported")

    # try to get paper from Firebase first
    paper = get_paper_from_db(paper_id)
    if paper:
        logger.debug("Paper found in database.")
        return paper
    else:
        logger.debug("Paper not found in database.")

    response = requests.get(paper_url)
    if response.status_code != 200:
        # TODO: to improve URL validation
        logger.error(f"Cannot connect to {paper_url}")
        raise Exception(f"Cannot connect to {paper_url}")

    # make soup
    soup = BeautifulSoup(response.text, "html.parser")

    # make paper dict 
    paper_dict = {
            "paper_id": paper_id,
            "paper_url": paper_url,
            "pdf_url": pdf_url,
        }

    ##### TITLE
    result = soup.find("h1", class_="title mathjax")
    tmp = [i.string for i in result]
    paper_title = tmp.pop()
    paper_dict["title"] = paper_title
    logger.debug(f"Paper Title: {paper_title}")
    ##### AUTHORS
    result = soup.find("div", class_="authors")
    author_list = [i.string.strip() for i in result]
    author_list.pop(0)
    while "," in author_list:
        author_list.remove(",")
    paper_dict["authors"] = author_list
    ##### ABSTRACT
    result = soup.find("blockquote", class_="abstract mathjax")
    tmp = [i.string for i in result]
    paper_abstract = tmp.pop()
    tmp = paper_abstract.split("\n")
    paper_abstract = " ".join(tmp)
    paper_dict["abstract"] = paper_abstract
    # logger.debug(f"Paper Abstract: {paper_abstract}")
    ##### COMMENTS
    result = soup.find("td", class_="tablecell comments mathjax")
    if result:
        comments = [i.string.strip() if i.string else "" for i in result]
        comments = " ".join(comments)
    else:
        comments = ""
    
    paper_dict["comments"] = comments

    # get a Paper object
    paper = Paper.from_dict(paper_dict)
    save_paper_to_db(paper)
    return paper


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


class TelegramUser:
    def __init__(self, username:str, first_name:str = "", last_name:str = ""):
        self.username : str = username
        self.first_name : str = first_name
        self.last_name : str = last_name
    

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
            "user_createdAt": timestamp_now(),
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
            "added_at": timestamp_now(),
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
    
    url = "https://arxiv.org/abs/2010.00514"
    pdfurl = "https://arxiv.org/pdf/1811.12432.pdf"
    paper = get_paper(url)
    # download_pdf(paper)
    print((paper))
