from html.parser import HTMLParser
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a":
            self.links.append(values.get("href"))
        if tag == "link" and values.get("rel") == "stylesheet":
            self.stylesheets.append(values.get("href"))


class SiteTest(TestCase):
    def setUp(self):
        self.source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.parser = PageParser()
        self.parser.feed(self.source)

    def test_local_assets_exist(self):
        for asset in self.parser.stylesheets:
            self.assertTrue((ROOT / asset).is_file(), asset)

    def test_primary_destinations_are_secure(self):
        external = [link for link in self.parser.links if link != "/"]
        self.assertTrue(external)
        self.assertTrue(all(link.startswith("https://") for link in external))

    def test_custom_domain_matches_landing_link(self):
        self.assertEqual((ROOT / "CNAME").read_text().strip(), "www.postproject.org")
        self.assertIn("https://docs.postproject.org/", self.parser.links)

