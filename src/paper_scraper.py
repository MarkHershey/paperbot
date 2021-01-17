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
from constants import project_root
from datautils import get_paper_from_db, save_paper_to_db
from paper_class import Paper
from url_handlers import process_url

__all__ = ["get_paper"]


def get_paper(url: str) -> Paper:
    """
    Get a Paper object from a supported URL
    """
    try:
        tmp_paper_dict = process_url(url)
    except Exception as err:
        logger.error(err)
        raise Exception(f"Error while processing URL: {url}")

    # verify expected keys are present
    for key in ("paper_id", "paper_url", "pdf_url", "src_website"):
        if not key in tmp_paper_dict:
            logger.error(f"Missing Key in 'tmp_paper_dict': {key}")
            raise Exception(f"Missing Key in 'tmp_paper_dict': {key}")

    # try to get paper from database first
    paper = get_paper_from_db(tmp_paper_dict["paper_id"])
    if paper:
        logger.debug("Paper found in database.")
        return paper
    else:
        logger.debug("Paper not found in database, start scraping...")

    # start scraping from source website
    src_website = tmp_paper_dict.get("src_website")
    if src_website == "arxiv":
        paper = get_paper_from_arxiv(tmp_paper_dict)
    elif src_website == "cvf":
        paper = get_paper_from_cvf(tmp_paper_dict)
    elif src_website == "openreview":
        paper = get_paper_from_openreview(tmp_paper_dict)
    else:
        logger.error(f"Invalid source website: '{src_website}'")
        raise Exception(f"Invalid source website: '{src_website}'")

    # save new paper to database
    save_paper_to_db(paper)

    return paper


def get_paper_from_arxiv(tmp_paper_dict: Dict[str, str]) -> Paper:
    paper_url = tmp_paper_dict.get("paper_url")
    response = requests.get(paper_url)

    if response.status_code != 200:
        logger.error(f"Cannot connect to {paper_url}")
        raise Exception(f"Cannot connect to {paper_url}")

    # make soup
    soup = BeautifulSoup(response.text, "html.parser")

    # get TITLE
    result = soup.find("h1", class_="title mathjax")
    tmp = [i.string for i in result]
    paper_title = tmp.pop()
    tmp_paper_dict["title"] = paper_title
    logger.debug(f"Paper Title: {paper_title}")

    # get AUTHORS
    result = soup.find("div", class_="authors")
    author_list = [i.string.strip() for i in result]
    author_list.pop(0)
    while "," in author_list:
        author_list.remove(",")
    tmp_paper_dict["authors"] = author_list

    # get ABSTRACT
    result = soup.find("blockquote", class_="abstract mathjax")
    tmp = [i.string for i in result]
    paper_abstract = tmp.pop()
    tmp = paper_abstract.split("\n")
    paper_abstract = " ".join(tmp)
    tmp_paper_dict["abstract"] = paper_abstract

    # get COMMENTS
    result = soup.find("td", class_="tablecell comments mathjax")
    if result:
        comments = [i.string.strip() if i.string else "" for i in result]
        comments = " ".join(comments)
    else:
        comments = ""
    tmp_paper_dict["comments"] = comments

    # return a Paper object
    return Paper.from_dict(tmp_paper_dict)


def get_paper_from_cvf(tmp_paper_dict: Dict[str, str]) -> Paper:
    pass


def get_paper_from_openreview(tmp_paper_dict: Dict[str, str]) -> Paper:
    pass
