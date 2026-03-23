import requests
from django.conf import settings
from knowledge_graph.neo4j_db import Neo4jConnection

class AIService:
    """AI助手服务类"""
    
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    
    SYSTEM_PROMPT = """你是一个专业的校史知识图谱AI助手，名字叫"成小理"。
你的任务是基于提供的数据库上下文信息，回答用户关于学校历史、人物、事件、机构等方面的问题。

回答原则：
1. **精准回答**：仔细分析用户意图，只回答用户问的具体点。
2. **绝对忠实**：**只能**使用提供的【数据库上下文】中的信息回答。如果上下文中没有提到某个人或事，必须直接说"数据库中暂时没有关于XXX的记录"，严禁编造或使用通用知识回答。
3. **排版清晰**：使用Markdown语法（加粗、列表）组织内容。
4. **语气友好**：使用亲切、活泼、自然的语气。

请谨记：你的知识仅限于提供的数据库上下文！"""

    @classmethod
    def _get_context(cls, question):
        """
        从知识图谱中检索相关上下文
        """
        try:
            # 改进的查询逻辑：
            # 1. 实体链接：问题包含实体名 (如 "张三是谁" 包含 "张三")
            # 2. 关键词搜索：实体名包含问题关键词 (如 "计算机" -> "计算机学院")
            # 3. 描述搜索：描述中包含问题关键词 (辅助补充)
            query = """
            MATCH (n:Entity)
            WHERE 
              (size(n.name) >= 2 AND toLower($question) CONTAINS toLower(n.name))
              OR 
              toLower(n.name) CONTAINS toLower($question)
              OR 
              toLower(n.description) CONTAINS toLower($question)
              OR 
              toLower(n.subtype) CONTAINS toLower($question)
            WITH n
            
            // 排序优化：优先完全匹配，其次是包含关系
            ORDER BY 
              CASE WHEN n.name = $question THEN 0 
                   WHEN size(n.name) > 2 AND toLower($question) CONTAINS toLower(n.name) THEN 1  // 实体链接优先
                   ELSE 2 END
            LIMIT 5

            // 获取一度关系
            OPTIONAL MATCH (n)-[r]-(m:Entity)
            RETURN n.name as name, n.description as description, n.type as type, n.subtype as subtype,
                   type(r) as relationship, m.name as neighbor, m.type as neighbor_type
            LIMIT 30
            """
            
            records = Neo4jConnection.query(query, {"question": question})
            
            if not records:
                # 如果没有找到记录，不要直接传空给 LLM，否则 LLM 容易根据名字编造
                # 尝试稍微放宽搜索或者直接返回无结果标记
                return ""
            
            context_parts = []
            seen_entities = set()
            
            for record in records:
                name = record['name']
                desc = record['description']
                subtype = record.get('subtype', '')
                neighbor = record['neighbor']
                rel = record['relationship']
                
                # 添加实体基本信息
                if name not in seen_entities:
                    seen_entities.add(name)
                    entity_info = f"实体: {name} (类型: {record['type']}"
                    if subtype:
                        entity_info += f", 细分类型: {subtype}"
                    entity_info += ")"
                    
                    if desc:
                        # 限制描述长度，但保留关键信息用于回答特定问题
                        entity_info += f"\n描述: {desc}"
                    context_parts.append(entity_info)
                
                # 添加关系信息
                if neighbor and rel:
                    context_parts.append(f"- 关系: {name} --[{rel}]--> {neighbor} ({record['neighbor_type']})")

            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"检索上下文出错: {e}")
            return ""

    @classmethod
    def _extract_likely_entities(cls, question):
        """
        简单的关键词提取逻辑（无需调用 LLM，降低成本）
        提取规则：
        1. 排除常用停用词（的、有、是、在、什么、哪些...）
        2. 保留可能的实体名
        """
        stop_words = ["的", "有", "是", "在", "什么", "哪些", "吗", "了", "和", "跟", "与", "介绍", "一下", "研究", "方向", "老师", "教授", "关于"]
        cleaned = question
        for sw in stop_words:
             cleaned = cleaned.replace(sw, " ")
        
        # 返回长度大于1的片段
        candidates = [w for w in cleaned.split() if len(w) > 1]
        return candidates

    @classmethod
    def ask(cls, question):
        """
        向AI助手提问
        :param question: 用户的问题
        :return: AI的回答
        """
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        
        # 1. 开发环境/无 Key 模式下的调试反馈
        if not api_key or api_key.startswith('sk-test') or len(api_key) < 10:
             context = cls._get_context(question)
             return f'AI助手正在配置中。需要配置有效的DeepSeek API密钥才能生成回答。\\n\\n检索到的数据库信息如下（仅供调试）：\\n{context if context else "未找到相关信息"}'
            
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 2. 第一次尝试：直接使用问题全文检索
        context = cls._get_context(question)
        
        # 3. 第二次尝试：如果第一次没找到，尝试提取关键词检索（解决“研究大语言模型的有哪些老师”这种长句匹配不到的问题）
        if not context:
            keywords = cls._extract_likely_entities(question)
            if keywords:
                # print(f"尝试使用关键词二次检索: {keywords}")
                for kw in keywords:
                    sub_context = cls._get_context(kw)
                    if sub_context:
                        context += f"\\n--- 来自关键词 '{kw}' 的检索结果 ---\\n{sub_context}"
                        # 限制一下，只要找到一点相关信息就停止，避免拼凑太多
                        if len(context) > 500: 
                            break
        
        final_system_prompt = cls.SYSTEM_PROMPT
        if context:
            final_system_prompt += f"\\n\\n数据库中检索到的相关背景信息（你必须**仅**基于此信息回答）：\\n{context}\\n\\n注意：如果数据库中只有提到某个方向的老师，但没有明确统计数量，你可以列出已知的老师，并说明'目前数据库中有记录的老师是这些'。"
        else:
            final_system_prompt += f"\\n\\n数据库中暂时没有关于用户问题的记录。请礼貌地告诉用户：'抱歉，校史数据库中暂时没有关于此问题的详细记录。您可以尝试更具体的关键词（如具体的人名或事件）。'"

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": final_system_prompt},
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
