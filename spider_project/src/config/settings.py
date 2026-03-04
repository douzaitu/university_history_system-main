# 目标页面URL（需替换为实际要爬取的导师列表页URL）
TARGET_URL = "https://cist.cdut.edu.cn/szdw/jsml.htm"
DATA_RAW_PATH = "../../data/raw/teacher_info.json"  # 数据保存路径
# 请求头（模拟浏览器，避免被识别为爬虫）
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, std",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "sMLAeTqisZbFO=60p6oEoq9cZNy6s4cLCHCUxYJYtetP2zADM5YPaTQnntLA6yfYaB65p77SGIT2zwDSdwaKxc.nSzl9nW5SEwRmfq; JSESSIONID=095CB3A891A3D2162504B6ED0DB050AC; sMLAeTqisZbFP=0NIbd82VKHKH_R4AVqhgxU0irOF.BAX1_Ki3g2NXD8N1.uxDAyFE4Ukgc.C0m2NsRjMFjD0QKV2Je_CcWSxfZ0JpZ.LqSuGBW3LytNYaKk06ECtivInWbHK4KjczLXqKy1AomQn7aw6OA_0wPn29xAy8v5i2Rhpde6aOvSEN2rjC8X8dAUfXQsV77knQ7sLKM3h7x3Ney8EVT4e6_LzWVW589ypHSUFzeKF_8XpI9YRzUHIGiBCQvZoiRUXfnv.QOl.909CwoJACUmqfVKV8kIU7ACOySRehvOk5bDiPUjh.98EnV5RpBy07hajILVMfDXYdbNsQEvnh8qsm1pusgvMQ1MpRX9NG5lks6vEKGCn40CYu0YsuFFCZICWIIGiVROeXllZ27qhrHLO_a8MkmBiFnC_jha0d1sb_uER9l0cjoN2lf9P0fY._wm7W0yuA32fjeL2W_JuXRd.L_zUGz0G",  # 关键！必须替换为实际Cookie
    "Host": "cist.cdut.edu.cn",
    "Referer": "https://cist.cdut.edu.cn/szdw/jsml.htm",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
}

# 数据存储路径
DATA_RAW_PATH = "../../data/raw/teacher_info.json"  # 相对路径，需确保目录存在