# built-in modules
import re
from pathlib import Path
from typing import Dict, List, Tuple

# external modules
from markkk.logger import logger


def process_arxiv_url(url: str) -> Tuple[str]:
    def get_paper_id_from_url(url) -> str:
        while "/" in url:
            slash_idx = url.find("/")
            url = url[slash_idx + 1 :]
        if url.endswith(".pdf"):
            return url[:-4]
        else:
            return url

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
        logger.error("Unexpected URL Error by arxiv URL Handler.")
        raise Exception("Unexpected URL Error by arxiv URL Handler.")


def process_cvf_url(url: str) -> Tuple[str]:
    """
    Open Access url can be splitted into 5 parts:
    start: 'https://openaccess.thecvf.com/'
    context: 'content_CVPR_2020/'
    pg_type: '/html/'
    name: 'Wang_Dual_Super-Resolution_Learning_for_Semantic_Segmentation_CVPR_2020_paper'
    end: '.html'
    ==> url = start + context + pg_type + name + end
    """

    # url validation
    if "openaccess.thecvf.com" not in url:
        logger.error("Unexpected URL Error by CVF URL Handler.")
        raise Exception("Unexpected URL Error by CVF URL Handler.")

    def get_paper_id(url) -> str:
        """
        Can parse either main url (paper_url) or pdf_url to find paper_id
        paper_id in the form of: (context + name)
        eg: "content_CVPR_2020/Wang_Dual_Super-Resolution_Learning_for_Semantic_Segmentation_CVPR_2020_paper"
        """
        while "/" in url:
            slash_idx = url.find("/")
            url = url[slash_idx + 1 :]
            # stop after slash until "content_CVPR..."
            flag = re.search("^content", url)
            if flag != None:
                break
        if url.endswith(".html"):
            paper_id = url.replace("/html", "").replace(".html", "")
            return paper_id
        else:
            paper_id = url.replace("/papers", "").replace(".pdf", "")
            return paper_id

    def get_pg_from_paper_id(paper_id: str, parse_mode="abs") -> str:
        start = "https://openaccess.thecvf.com/"
        context, name = paper_id.split("/")
        if parse_mode == "abs":
            pg_type = "/html/"
            end = ".html"
        elif parse_mode == "pdf":
            pg_type = "/papers/"
            end = ".pdf"
        else:
            raise Exception("parse_mode error")

        url = start + context + pg_type + name + end
        return url

    paper_id = get_paper_id(url)
    if "/html" in url:
        ## abstract page
        paper_url = url
        pdf_url = get_pg_from_paper_id(paper_id, parse_mode="pdf")
        return paper_id, paper_url, pdf_url
    elif "/papers" in url:
        ## pdf page
        paper_url = get_pg_from_paper_id(paper_id, parse_mode="abs")
        pdf_url = url
        return paper_id, paper_url, pdf_url
    else:
        logger.error("Unexpected URL Error by CVF URL Handler.")
        raise Exception("Unexpected URL Error by CVF URL Handler.")


def process_openreview_url(url: str) -> Tuple[str]:
    """
    Open Review url can be splitted into 5 parts:
    start: 'https://openreview.net/'
    pg_type: 'forum' or 'pdf'
    mid: '?id='
    paper_id: 'nlAxjsniDzg'
    ==> url = start + pg_type + mid + paper_id
    """

    # url validation
    if "openreview.net" not in url:
        logger.error("Unexpected URL Error by openreview URL Handler.")
        raise Exception("Unexpected URL Error by openreview URL Handler.")

    def get_paper_id(url) -> str:
        while "/" in url:
            slash_idx = url.find("/")
            url = url[slash_idx + 1 :]
        idx = url.find("=")
        paper_id = url[idx + 1 :]
        return paper_id

    def get_pg_from_paper_id(paper_id: str, parse_mode="abs") -> str:
        start = "https://openreview.net/"
        mid = "?id="
        if parse_mode == "abs":
            pg_type = "forum"
        elif parse_mode == "pdf":
            pg_type = "pdf"
        else:
            raise Exception("parse_mode error")
        url = start + pg_type + mid + paper_id
        return url

    paper_id = get_paper_id(url)
    if "forum" in url:
        ## abstract page
        paper_url = url
        pdf_url = get_pg_from_paper_id(paper_id, parse_mode="pdf")
        return paper_id, paper_url, pdf_url
    elif "pdf" in url:
        ## pdf page
        paper_url = get_pg_from_paper_id(paper_id, parse_mode="abs")
        pdf_url = url
        return paper_id, paper_url, pdf_url
    else:
        logger.error("Unexpected URL Error by openreview URL Handler.")
        raise Exception("Unexpected URL Error by openreview URL Handler.")


if __name__ == "__main__":
    from pprint import pprint

    pprint(process_arxiv_url("https://arxiv.org/abs/1301.3781"))
    pprint(
        process_cvf_url(
            "https://openaccess.thecvf.com/content_CVPR_2020/papers/Kim_Advisable_Learning_for_Self-Driving_Vehicles_by_Internalizing_Observation-to-Action_Rules_CVPR_2020_paper.pdf"
        )
    )
    pprint(process_openreview_url("https://openreview.net/forum?id=H1lj0nNFwB"))
