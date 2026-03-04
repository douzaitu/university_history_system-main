import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.config.settings import HEADERS

def get_html(url, headers=None, timeout=10):  # 新增headers参数
    try:
        if headers is None:
            headers = HEADERS  # 若未传入，使用配置的默认请求头
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.RequestException as e:
        logger.error(f"请求{url}失败：{e}")
        return None