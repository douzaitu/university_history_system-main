import os
import json
import requests
from django.conf import settings

# 简单的 LLM 桥接服务，用于统一调用 Ollama 或 DeepSeek
# 避免在不同地方写死不同的调用逻辑

class LLMBridge:
    @staticmethod
    def extract_entities(text, teacher_name, entity_types):
        """
        提取实体
        :param text: 待处理文本
        :param teacher_name: 导师姓名（作为上下文）
        :param entity_types: 需要提取的实体类型列表
        :return: 字典格式的实体数据
        """
        # 优先使用配置的 Ollama (本地且免费)，如果失败或者配置了 DeepSeek 且强制使用云端，可以切换
        # 目前保持原来的逻辑：提取使用 Ollama (Cheap & Fast for bulk)，问答使用 DeepSeek (Smart)
        
        # 构造 Prompt
        prompt = f"""
仅返回合法的 JSON 格式，不要包含任何 Markdown 标记或多余解释！
任务：从下面的文本中提取以下类型的实体：{', '.join(entity_types)}。
已知导师姓名：{teacher_name}
文本内容：
{text}

请输出类似如下的 JSON 格式：
{{
    "教师姓名": ["{teacher_name}"], 
    "院系": ["xxx学院"], 
    "职称": ["教授"], 
    "研究方向": ["xxx"], 
    "课程名称": [], 
    "毕业院校": [], 
    "荣誉称号": [], 
    "工作职责": []
}}
"""
        
        try:
            # 尝试导入 ollama 库
            import ollama
            model_name = getattr(settings, 'OLLAMA_MODEL', 'qwen2:7b')
            
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={"temperature": 0.1, "max_tokens": 1000}
            )
            
            content = response.get("response", "").strip()
            return LLMBridge._parse_json(content)
            
        except ImportError:
            # 如果没有 ollama 库，尝试使用 requests 调用 Ollama API
            try:
                model_name = getattr(settings, 'OLLAMA_MODEL', 'qwen2:7b')
                resp = requests.post('http://localhost:11434/api/generate', json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                }, timeout=60)
                if resp.status_code == 200:
                    content = resp.json().get("response", "").strip()
                    return LLMBridge._parse_json(content)
            except Exception as e:
                print(f"Ollama API call failed: {e}")

        except Exception as e:
            print(f"Ollama generation failed: {e}")
            
        # Fallback: 如果 Ollama 失败，或者你想用 DeepSeek 做提取（更贵但更准）
        # 这里暂时只返回基础数据作为 fallback
        return {"教师姓名": [teacher_name]}

    @staticmethod
    def _parse_json(content):
        """尝试解析各种不规范的 JSON 返回"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except:
            pass
        
        import re
        try:
            # 尝试提取 ```json ... ``` 或 {...}
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                json_str = match.group()
                return json.loads(json_str)
        except:
            pass
            
        print(f"Failed to parse JSON from LLM response: {content[:100]}...")
        return {}
