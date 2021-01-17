import sys
import unittest
from pathlib import Path

import requests

# get project root
project_root: Path = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"
# add src into path
sys.path.insert(0, str(src_dir))

from url_handlers import process_arxiv_url, process_cvf_url, process_openreview_url

_arxiv_urls = [
    "https://arxiv.org/abs/1405.4053",
    "https://arxiv.org/pdf/2101.05725.pdf",
    "https://arxiv.org/abs/2101.05709",
]


class TestUrlHandlers(unittest.TestCase):
    def test_process_arxiv_url(self):
        for i in _arxiv_urls:
            _, paper_url, pdf_url = process_arxiv_url(i)
            response = requests.get(paper_url)
            self.assertEqual(response.status_code, 200)
            response = requests.get(pdf_url)
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
