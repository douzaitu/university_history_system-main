import os
import json
import requests
from django.conf import settings

# 简单的 LLM 桥接服务，用于统一调用 Ollama 或 DeepSeek
# 避免在不同地方写死不同的调用逻辑

class LLMBridge:
    @staticmethod
    def extract_primary_entity_info(text, category):
        """
        通用提取：从一段文本中提取主要实体的 名称 和 简要描述
        :param text: 待处理文本（例如 Excel 的一行数据合并后的字符串）
        :param category: 实体类型（person, location, event, organization 等）
        :return: {"name": "...", "description": "..."}
        """
        category_name_map = {
            'person': '人物',
            'location': '地点/建筑',
            'event': '事件',
            'organization': '机构/组织',
            'subject': '学科',
            'general': '实体'
        }
        target_entity = category_name_map.get(category, '实体')
        
        # 根据不同类型提供针对性的示例，避免模型被误导
        examples_map = {
            'person': '{\n    "name": "蔡彪",\n    "description": "教授，计算机与网络安全学院院长。男，1970年出生。研究方向为人工智能。......"\n}',
            'location': '{\n    "name": "图书馆",\n    "description": "位于校园中心，建于1995年，共5层，藏书100万册。是学校标志性建筑之一。"\n}',
            'event': '{\n    "name": "建校50周年校庆",\n    "description": "2005年9月举办，邀请了众多校友回校。举办了文艺晚会、学术讲座等系列活动。"\n}',
            'organization': '{\n    "name": "计算机学院",\n    "description": "成立于1980年，现有教职工100余人，拥有3个国家级重点实验室。"\n}',
            'subject': '{\n    "name": "计算机科学与技术",\n    "description": "国家一级学科，涵盖软件工程、人工智能等方向。2018年入选双一流建设学科。"\n}'
        }
        
        example_json = examples_map.get(category, examples_map['person'])
        
        # 针对事件类型增加额外的约束提示，防止提取成人名
        extra_instruction = ""
        if category == 'event':
            extra_instruction = "重要提示：提取的【名称】必须是事件本身的名称（如xx会议、xx讲座、xx活动、xx比赛），绝对不要提取任何参与该事件的人名作为实体名称！"
        elif category == 'organization':
            extra_instruction = "重要提示：提取的【名称】必须是机构的全称，不要提取负责人或领导的名字。"
        
        prompt = f"""
任务：从下面的文本中提取一个【{target_entity}】的核心信息。
文本内容：
{text}

要求：
1. **最高优先级**：如果文本开头包含类似 【实体名称：XXX】 的标记，请直接使用 XXX 作为实体名称，不要自己从正文中重新归纳或提取其他实体。
2. 提取实体名称（Name）和描述（Description）。
3. 如果文本中有关于该实体的详细信息（如经历、职务、时间、地点、背景等），请尽量完整地保留在 description 中，不要进行过度缩减或概括。
4. 如果文本中包含多个实体，请提取与【{target_entity}】最相关的主体。
5. {extra_instruction}
6. 如果无法提取有效信息，请返回空字符串。
7. 仅返回合法的 JSON 格式，不要包含 Markdown 标记。

JSON 格式示例：
{example_json}
"""
        return LLMBridge._call_llm(prompt)

    @staticmethod
    def _call_llm(prompt):
        """统一调用 LLM 的底层逻辑"""
        try:
            # 尝试导入 ollama 库
            import ollama
            model_name = getattr(settings, 'OLLAMA_MODEL', 'qwen2:7b') # 默认使用 qwen2:7b
            
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
                return {}

        except Exception as e:
            print(f"Ollama generation failed: {e}")
            return {}

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
        
        result = LLMBridge._call_llm(prompt)
        if not result:
             return {"教师姓名": [teacher_name]}
        return result

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
