from bs4 import BeautifulSoup
from loguru import logger

def parse_teacher_info(html):
    """解析导师信息页面，提取导师姓名、职称等数据"""

    soup = BeautifulSoup(html, "html.parser")
    leader_data = {}
    # 提取姓名和职务
    title_tag = soup.find("div", class_="title").find("h3")
    if title_tag:
        leader_data["name_title"] = title_tag.get_text(strip=True)
    # 提取职责
    content_tag = soup.find("div", class_="v_news_content")
    if content_tag:
        duty_p = content_tag.find("p", style=lambda x: x and "text-indent: 37px" in x)
        leader_data["duty"] = duty_p.get_text(strip=True) if duty_p else "未标注职责"
    # 提取头像URL
    img_tag = content_tag.find("img", class_="img_vsb_content")
    if img_tag:
        leader_data["avatar_url"] = img_tag.get("src")
    return leader_data