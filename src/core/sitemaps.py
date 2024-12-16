from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class HomeSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return ["dashboard", "uploads", "login", "new_game", "signup"]

    def location(self, item):
        return reverse(item)
