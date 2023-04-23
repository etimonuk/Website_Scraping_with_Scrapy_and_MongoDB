import scrapy
from ..items import (
    LogrocketArticleItem,
    LogrocketArticleCommentItem
)


class FeatureArticleSpider(scrapy.Spider):
    name = "feature_article"
    allowed_domains = ["blog.logrocket.com"]
    start_urls = ["http://blog.logrocket.com/"]

    def parse(self, response):
        feature_articles = response.css("section.featured-posts div.card")
        for article in feature_articles:
            article_dict = {
                "heading": article.css("h2.card-title a::text").extract_first().strip(),
                "url": article.css("h2.card-title a::attr(href)").extract_first(),
                "author": article.css("span.author-meta span.post-name a::text").extract_first(),
                "published_on": article.css("span.author-meta span.post-date::text").extract_first(),
                "read_time": article.css("span.readingtime::text").extract_first(),
            }
            yield article_dict

    def get_comments(self, response):
        """
        The callback method gets the response from each article url.
        It fetches the article comment obj, creates a list of comments, and returns dict with the list of comments and article id.
        """
        article_comments = response.css("ol.comment-list li")
        comments = list()
        for comment in article_comments:
            comment_obj = LogrocketArticleCommentItem(
                _id=comment.css("::attr('id')").extract_first(),
                # special case: author can be inside `a` or `b` tag, so using xpath
                author=comment.xpath("string(//div[@class='comment-author vcard']//b)").get(),
                # special case: there can be multiple p tags, so for fetching all p tag inside content, xpath is used.
                content=comment.xpath("string(//div[@class='comment-content']//p)").get(),
                published=comment.css("div.comment-metadata a time::text").extract_first(),
            )
            comments.append(comment_obj)

        yield {"comments": comments, "article_id": response.meta.get("article_id")}

    def get_article_obj(self, article):
        """
        Creates an ArticleItem by populating the item values.
        """
        article_obj = LogrocketArticleItem(
            _id=article.css("::attr('id')").extract_first(),
            heading=article.css("h2.card-title a::text").extract_first(),
            url=article.css("h2.card-title a::attr(href)").extract_first(),
            author=article.css("span.author-meta span.post-name a::text").extract_first(),
            published_on=article.css("span.author-meta span.post-date::text").extract_first(),
            read_time=article.css("span.readingtime::text").extract_first(),
        )
        return article_obj

    def parse(self, response):
        """
        Main Method: loop through each article and yield the article.
        Also raises a request with the article url and yields the same
        :param response:
        :return:
        """
        feature_articles = response.css("section.featured-post div.card")
        for article in feature_articles:
            article_obj = self.get_article_obj(article)
            # yield the article object
            yield article_obj
            # yield the comments for the article
            yield scrapy.Request(
                url = article_obj.url,
                callback=self.get_comments,
                meta={
                    "article_id": article_obj.id,
                }
            )
