# built-in modules
from pathlib import Path
from typing import List, Dict, Tuple


class Paper:
    def __init__(
        self,
        paper_uid="",
        paper_id="",
        title="",
        authors=[],
        paper_url="",
        pdf_url="",
        abstract="",
        one_sentence_summary="",
        keywords=[],
        public_comments="",
        year="",
        published_at="",
        bibtex="",
        source_site="",
    ):
        self.paper_uid = paper_uid
        self.paper_id: str = paper_id
        self.title: str = title
        self.authors: List[str] = authors
        self.paper_url: str = paper_url
        self.pdf_url: str = pdf_url
        self.abstract: str = abstract
        self.one_sentence_summary: str = one_sentence_summary
        self.keywords: List[str] = keywords
        self.public_comments: str = public_comments
        self.year: str = year
        self.published_at: str = published_at
        self.bibtex: str = bibtex
        self.source_site: str = source_site

        # derived
        self.first_author = self.authors[0] if self.authors else ""

    def __repr__(self) -> str:
        return self.title

    def to_dict(self) -> dict:
        _dict = {
            "paper_uid": self.paper_uid,
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "paper_url": self.paper_url,
            "pdf_url": self.pdf_url,
            "abstract": self.abstract,
            "one_sentence_summary": self.one_sentence_summary,
            "keywords": self.keywords,
            "public_comments": self.public_comments,
            "year": self.year,
            "published_at": self.published_at,
            "bibtex": self.bibtex,
            "source_site": self.source_site,
            "first_author": self.first_author,
        }
        return _dict

    @staticmethod
    def from_dict(src_dict: dict):
        #TODO: dict validations

        return Paper(
            paper_uid=src_dict.get("paper_uid", ""),
            paper_id=src_dict.get("paper_id", ""),
            title=src_dict.get("title", ""),
            authors=src_dict.get("authors", []),
            paper_url=src_dict.get("paper_url", ""),
            pdf_url=src_dict.get("pdf_url", ""),
            abstract=src_dict.get("abstract", ""),
            one_sentence_summary=src_dict.get("one_sentence_summary", ""),
            keywords=src_dict.get("keywords", []),
            public_comments=src_dict.get("public_comments", ""),
            year=src_dict.get("year", ""),
            published_at=src_dict.get("published_at", ""),
            bibtex=src_dict.get("bibtex", ""),
            source_site=src_dict.get("source_site", ""),
        )

    def get_first_author(self) -> str:
        return self.authors[0] if self.authors else None

    