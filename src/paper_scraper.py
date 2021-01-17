# built-in modules
import json
from pathlib import Path
from typing import Dict, List, Tuple

# external modules
import requests
from bs4 import BeautifulSoup
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
        paper_dict = get_paper_from_arxiv(tmp_paper_dict)
    elif src_website == "cvf":
        paper_dict = get_paper_from_cvf(tmp_paper_dict)
    elif src_website == "openreview":
        paper_dict = get_paper_from_openreview(tmp_paper_dict)
    else:
        logger.error(f"Invalid source website: '{src_website}'")
        raise Exception(f"Invalid source website: '{src_website}'")

    # get paper object
    paper = Paper.from_dict(paper_dict)
    # save new paper to database
    save_paper_to_db(paper)

    return paper


def get_paper_from_arxiv(tmp_paper_dict: Dict[str, str]) -> Dict[str, str]:
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

    return tmp_paper_dict


def get_paper_from_cvf(tmp_paper_dict: Dict[str, str]) -> Dict[str, str]:
    paper_url = tmp_paper_dict.get("paper_url")
    response = requests.get(paper_url)

    if response.status_code != 200:
        logger.error(f"Cannot connect to {paper_url}")
        raise Exception(f"Cannot connect to {paper_url}")

    # make soup
    soup = BeautifulSoup(response.text, "html.parser")

    # get TITLE
    result = soup.find("div", id="papertitle")
    tmp = [i.string for i in result]
    paper_title = tmp.pop()
    tmp_paper_dict["title"] = paper_title.strip()

    # get AUTHORS
    result = soup.find("div", id="authors")
    main_content = str(result.contents[2])
    authors_str = main_content[6:-8]
    author_list = [author.lstrip() for author in authors_str.split(",")]
    tmp_paper_dict["authors"] = author_list

    # get ABSTRACT
    result = soup.find("div", id="abstract")
    tmp = [i.string for i in result]
    paper_abstract = tmp.pop()
    tmp = paper_abstract.split("\n")
    paper_abstract = " ".join(tmp)
    tmp_paper_dict["abstract"] = paper_abstract.lstrip()

    # get Bibtex
    result = str(soup.find("div", {"class": "bibref"}))
    bibtex = result[21:-6]
    bibtex = bibtex.replace("<br/>", "")
    tmp_paper_dict["bibtex"] = bibtex

    return tmp_paper_dict


def get_paper_from_openreview(tmp_paper_dict: Dict[str, str]) -> Dict[str, str]:
    paper_url = tmp_paper_dict.get("paper_url")
    response = requests.get(paper_url)

    if response.status_code != 200:
        logger.error(f"Cannot connect to {paper_url}")
        raise Exception(f"Cannot connect to {paper_url}")

    # make soup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ref: https://stackoverflow.com/questions/52392246/how-to-convert-class-bs4-element-resultset-to-json-in-python-using-builtin-o
    # All data json
    result = soup.find("script", id="__NEXT_DATA__")
    tmp = [i.string for i in result]
    all_data_bs4 = tmp.pop()
    # convert to json/dict
    all_data_json = json.loads(str(all_data_bs4))
    # The "props" dict will contain all useful info
    data_dict = all_data_json["props"]["pageProps"]["forumNote"]["content"]

    # get TITLE
    tmp_paper_dict["title"] = data_dict.get("title", "")
    # get KEYWORDS
    tmp_paper_dict["keywords"] = data_dict.get("keywords", "")
    # get AUTHORS
    tmp_paper_dict["authors"] = data_dict.get("authors", "")
    # get ABSTRACT
    tmp_paper_dict["abstract"] = data_dict.get("abstract", "")
    # get TL;DR
    if data_dict.get("one-sentence_summary"):
        tmp_paper_dict["tldr"] = data_dict.get("one-sentence_summary", "")
    else:
        tmp_paper_dict["tldr"] = data_dict.get("TL;DR", "")
    # get Bibtex
    tmp_paper_dict["bibtex"] = data_dict.get("_bibtex", "")

    return tmp_paper_dict


if __name__ == "__main__":
    from pprint import pprint

    # pprint(get_paper_from_arxiv(process_url("https://arxiv.org/abs/1301.3781")))
    # pprint(get_paper_from_cvf(process_url("https://openaccess.thecvf.com/content_CVPR_2020/papers/Kim_Advisable_Learning_for_Self-Driving_Vehicles_by_Internalizing_Observation-to-Action_Rules_CVPR_2020_paper.pdf")))
    # pprint(get_paper_from_openreview(process_url("https://openreview.net/forum?id=H1lj0nNFwB")))
    pprint(get_paper("https://arxiv.org/abs/1301.3781"))