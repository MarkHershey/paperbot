import os
import re
import json
import base64
from pathlib import Path
from typing import List, Dict, Tuple

from data.utils import *

import requests
from bs4 import BeautifulSoup
from markkk.logger import logger

project_root = Path(__file__).resolve().parent.parent
papers_dir = project_root / "papers"
assert papers_dir.is_dir()


class Paper:
    def __init__(
        self,
        paper_id="",
        title="",
        authors=[""],
        abs_url="",
        pdf_url="",
        abstract="",
        comments="",
    ):
        self.paper_id: str = paper_id
        self.title: str = title
        self.authors: List[str] = authors
        self.abs_url: str = abs_url
        self.pdf_url: str = pdf_url
        self.abstract: str = abstract
        self.comments: str = comments
        # derived
        self.first_author = self.authors[0]

    def __repr__(self):
        return self.title

    def to_dict(self):
        _dict = {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "abs_url": self.abs_url,
            "pdf_url": self.pdf_url,
            "abstract": self.abstract,
            "comments": self.comments,
        }
        return _dict

    @staticmethod
    def from_dict(src: dict) -> Dict:
        return Paper(
            paper_id=src.get("paper_id"),
            title=src.get("title"),
            authors=src.get("authors"),
            abs_url=src.get("abs_url"),
            pdf_url=src.get("pdf_url"),
            abstract=src.get("abstract"),
            comments=src.get("comments"),
        )


def process_url(url: str) -> Tuple[str]:
    # TODO: Validate URL

    if "arxiv.org/abs" in url:
        ## abstract page
        paper_id = get_paper_id_from_url(url)
        abs_url = url
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        return paper_id, abs_url, pdf_url
    elif "arxiv.org/pdf" in url:
        ## pdf page
        paper_id = get_paper_id_from_url(url)
        abs_url = f"https://arxiv.org/abs/{paper_id}"
        pdf_url = url
        return paper_id, abs_url, pdf_url
    else:
        logger.error("URL not supported")
        raise Exception("URL not supported")


def get_paper_id_from_url(url) -> str:
    while "/" in url:
        slash_idx = url.find("/")
        url = url[slash_idx + 1 :]

    if url.endswith(".pdf"):
        return url[:-4]
    else:
        return url


def get_paper(url: str) -> Paper:
    try:
        paper_id, abs_url, pdf_url = process_url(url)
    except Exception as err:
        logger.error(err)
        raise Exception("URL not supported")

    # try to get paper from Firebase first
    paper = get_paper_db(paper_id)
    if paper:
        logger.debug("Paper found in database.")
        return paper
    else:
        logger.debug("Paper not found in database.")

    response = requests.get(abs_url)
    if response.status_code != 200:
        # TODO: to improve URL validation
        logger.error(f"Cannot connect to {abs_url}")
        raise Exception(f"Cannot connect to {abs_url}")

    # make soup
    soup = BeautifulSoup(response.text, "html.parser")

    ##### TITLE
    result = soup.find("h1", class_="title mathjax")
    tmp = [i.string for i in result]
    paper_title = tmp.pop()
    logger.debug(f"Paper Title: {paper_title}")
    ##### AUTHORS
    result = soup.find("div", class_="authors")
    author_list = [i.string.strip() for i in result]
    author_list.pop(0)
    while "," in author_list:
        author_list.remove(",")
    ##### ABSTRACT
    result = soup.find("blockquote", class_="abstract mathjax")
    tmp = [i.string for i in result]
    paper_abstract = tmp.pop()
    tmp = paper_abstract.split("\n")
    paper_abstract = " ".join(tmp)
    # logger.debug(f"Paper Abstract: {paper_abstract}")
    ##### COMMENTS
    result = soup.find("td", class_="tablecell comments mathjax")
    if result:
        comments = [i.string.strip() if i.string else "" for i in result]
        comments = " ".join(comments)
    else:
        comments = ""

    # get a Paper object
    paper = Paper(
        paper_id=paper_id,
        title=paper_title,
        authors=author_list,
        abs_url=abs_url,
        pdf_url=pdf_url,
        abstract=paper_abstract,
        comments=comments,
    )
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


if __name__ == "__main__":
    from data.utils import save_paper

    url = "https://arxiv.org/abs/2010.00514"
    pdfurl = "https://arxiv.org/pdf/1811.12432.pdf"
    paper = get_paper(url)
    # download_pdf(paper)
    print((paper))
