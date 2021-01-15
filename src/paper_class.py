# built-in modules
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


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
    def from_dict(src_dict: dict) -> Paper:
        # TODO: dict validations

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


class UserPaper:
    def __init__(
        self,
        paper_uid: str = "",
        reading_note: str = "",
        reading_status: str = "",
        labels: List[str] = [],
        added_at: datetime = None,
        last_read_at: datetime = None,
        favorite: bool = False,
    ):
        self.paper_uid: str = paper_uid
        self.reading_note: str = reading_note
        self.reading_status: str = reading_status
        self.labels: List[str] = labels
        self.added_at: datetime = datetime.now() if added_at is None else added_at
        self.last_read_at: datetime = (
            self.added_at if last_read_at is None else last_read_at
        )
        self.favorite: bool = favorite

    def favorite(self) -> None:
        self.favorite = True

    def unfavorite(self) -> None:
        self.favorite = False

    def toggle_favorite(self) -> None:
        self.favorite = False if self.favorite else True

    def update_reading_note(self, reading_note: str) -> None:
        self.reading_note = reading_note

    def add_label(self, label: str) -> None:
        if not isinstance(label, str):
            raise ValueError("label must be a string")
        if label not in self.labels:
            self.labels.append(label)

    def remove_label(self, label: str) -> None:
        if not isinstance(label, str):
            raise ValueError("label must be a string")
        if label in self.labels:
            self.labels.remove(label)

    def update_last_read(self, last_read_at: datetime) -> None:
        if not isinstance(last_read_at, datetime):
            raise ValueError("last_read_at must be a datetime object")
        self.last_read_at = last_read_at

    def to_dict(self) -> dict:
        _dict = {
            "paper_uid": self.paper_uid,
            "reading_note": self.reading_note,
            "reading_status": self.reading_status,
            "labels": self.labels,
            "added_at": self.added_at,
            "last_read_at": self.last_read_at,
            "favorite": self.favorite,
        }
        return _dict

    @staticmethod
    def from_dict(src_dict: dict) -> UserPaper:
        # TODO: dict validations

        return UserPaper(
            paper_uid=src_dict.get("paper_uid", ""),
            reading_note=src_dict.get("reading_note", ""),
            reading_status=src_dict.get("reading_status", ""),
            labels=src_dict.get("labels", []),
            added_at=src_dict.get("added_at", None),
            last_read_at=src_dict.get("last_read_at", None),
            favorite=src_dict.get("favorite", False),
        )
