from crawlers.teacher_crawler import TeacherCrawler
from loguru import logger

if __name__ == "__main__":
    logger.info("===== 启动爬虫项目 =====")
    crawler = TeacherCrawler()
    crawler.crawl()
    logger.info("= ==== 爬虫项目执行完毕 =====")