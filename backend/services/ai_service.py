import requests
from django.conf import settings

class AIService:
    """AI助手服务类"""
    
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    
    SYSTEM_PROMPT = """你是一个校史知识图谱AI助手。你的任务是：
    1. 回答关于学校历史、人物、事件、机构等问题
    2. 帮助用户理解知识图谱数据
    3. 提供友好的帮助和指导
    4. 如果不知道答案，可以引导用户到相关页面查看
    
    当前系统包含教师信息、学院机构、历史事件等数据。
    你可以根据用户的问题提供相关信息和指导。"""

    @classmethod
    def ask(cls, question):
        """
        向AI助手提问
        :param question: 用户的问题
        :return: AI的回答
        """
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        
        if not api_key or api_key == 'sk-test12345678901234567890':
            return 'AI助手正在配置中，请稍后再试。如需立即使用，请配置正确的DeepSeek API密钥。'
            
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": cls.SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            "stream": False,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                cls.DEEPSEEK_API_URL, 
                headers=headers, 
                json=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"API请求失败: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', error_msg)
                    except:
                        pass
                return f'抱歉，AI助手暂时无法回答。错误信息: {error_msg}。请检查API密钥是否正确。'
                
        except Exception as e:
            return f'AI助手遇到问题: {str(e)}。请稍后再试。'

# 全局实例
ai_service = AIService()
