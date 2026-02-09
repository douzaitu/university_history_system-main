import os
import pandas as pd
import json
import re
from neo4j import GraphDatabase, exceptions
import ollama
import sys
from collections import defaultdict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# -------------------------- DJANGO SETUP --------------------------
# 添加 backend 目录到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
    from knowledge_graph.models import Entity, Relationship
    print("✅ Django environment loaded successfully")
except Exception as e:
    print(f"⚠️ Failed to load Django environment: {e}")
    print("Sync to SQLite will be disabled.")
    Entity = None
    Relationship = None

# -------------------------- 核心配置（增强约束）--------------------------
CONFIG = {
    "excel_path": "",
    "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "neo4j_username": os.getenv("NEO4J_USERNAME", "neo4j"),
    "neo4j_password": os.getenv("NEO4J_PASSWORD", "12345678"),
    "ollama_model": "qwen2:7b",  # 更稳定的模型
    "max_text_length": 1500,
    "entity_types": [
        "教师姓名", "院系", "职称", "研究方向", "课程名称", "毕业院校", "荣誉称号", "工作职责"
    ],
    "predefined_relations": [
        "属于", "拥有", "研究", "主讲", "毕业于", "获得", "负责"
    ],
    "relation_mapping": {  # 明确关系-实体类型映射
        "属于": "院系",
        "拥有": "职称",
        "研究": "研究方向",
        "主讲": "课程名称",
        "毕业于": "毕业院校",
        "获得": "荣誉称号",
        "负责": "工作职责"
    }
}


# -------------------------- 1. LLM增强的实体提取 --------------------------
def llm_enhance_entities(teacher_name, full_text):
    """用LLM修正/补充实体提取结果，处理正则无法覆盖的复杂句式"""
    prompt = f"""
仅返回JSON，无多余内容！
任务：从文本中提取{', '.join(CONFIG['entity_types'])}，修正不完整实体，补充遗漏实体。
注意：包含"负责"、"主持"、"分管"等词的内容归类为"工作职责"，不要归类为"荣誉称号"！
已知导师姓名：{teacher_name}
文本：{full_text[:CONFIG['max_text_length']]}
输出格式：{{"教师姓名": ["{teacher_name}"], "院系": [], "职称": [], "研究方向": [], "课程名称": [], "毕业院校": [], "荣誉称号": [], "工作职责": []}}
"""
    try:
        response = ollama.generate(
            model=CONFIG["ollama_model"],
            prompt=prompt,
            options={"temperature": 0.1, "max_tokens": 300}
        )
        # 提取并解析JSON
        json_str = re.search(r"\{.*\}", response["response"].strip(), re.DOTALL).group()
        llm_entities = json.loads(json_str)
        # 转换为(实体, 类型)格式
        result = []
        for ent_type, ents in llm_entities.items():
            for ent in ents:
                if ent and ent.strip() and (ent.strip(), ent_type) not in result:
                    result.append((ent.strip(), ent_type))
        return result
    except Exception as e:
        print(f"LLM实体增强失败，使用原始提取：{e}")
        return extract_entities_from_text_v3(teacher_name, full_text)


def extract_entities_from_text_v3(teacher_name, full_text):
    """原始实体提取函数（作为LLM失败的备用）"""
    entities = []
    # 院校补全映射表（更全面）
    school_mapping = {
        "成都理工大": "成都理工大学",
        "四川大": "四川大学",
        "电子科技大": "电子科技大学",
        "日本九州大": "日本九州大学",
        "西南交通大": "西南交通大学",
        "成都理工学": "成都理工大学",
        "清华大": "清华大学",
        "北京大": "北京大学",
        "复旦大": "复旦大学"
    }

    # 应用院校补全
    for short, full in school_mapping.items():
        full_text = full_text.replace(short, full)

    # 1. 教师姓名（强制添加）
    if teacher_name and len(teacher_name.strip()) >= 2:
        entities.append((teacher_name.strip(), "教师姓名"))

    # 2. 职称（更精准的正则）
    title_pattern = r"(教授|副教授|讲师|助教|研究员|副研究员|高级实验师|工程师)"
    title_matches = re.findall(title_pattern, full_text)
    for title in title_matches:
        if title and (title, "职称") not in entities:
            entities.append((title, "职称"))

    # 3. 院系（更严格的匹配）
    dept_patterns = [
        r"([^，。；：\(\)（）]{2,10}[院系学院])",
        r"隶属于([^，。；：\(\)（）]{2,10}[院系学院])",
        r"主持([^，。；：\(\)（）]{2,10}[院系学院])"
    ]
    for pattern in dept_patterns:
        dept_matches = re.findall(pattern, full_text)
        for match in dept_matches:
            dept = match if isinstance(match, str) else match[0]
            dept = dept.strip()
            if dept and len(dept) >= 4 and any(x in dept for x in ["院", "系"]) and (dept, "院系") not in entities:
                entities.append((dept, "院系"))

    # 4. 工作职责（新增）
    work_patterns = [
        r"负责([^，。；：\(\)（）]{5,80})",
        r"主持([^，。；：\(\)（）]{5,80}工作)",
        r"分管([^，。；：\(\)（）]{5,80})"
    ]
    for pattern in work_patterns:
        work_matches = re.findall(pattern, full_text)
        for work in work_matches:
            work = work.strip()
            if len(work) > 30:
                works = re.split(r"、|，", work)
                for w in works:
                    w = w.strip()
                    if w and len(w) >= 3 and len(w) <= 20 and (w, "工作职责") not in entities:
                        entities.append((w, "工作职责"))
            elif work and len(work) >= 3 and (work, "工作职责") not in entities:
                entities.append((work, "工作职责"))

    # 5. 研究方向（分割多个方向）
    research_patterns = [
        r"研究方向[为：:\s]*([^，。；：\(\)（）]{5,50})",
        r"研究领域[为：:\s]*([^，。；：\(\)（）]{5,50})"
    ]
    for pattern in research_patterns:
        research_matches = re.findall(pattern, full_text)
        for research in research_matches:
            # 分割多个研究方向
            directions = re.split(r"[,，、;；]", research)
            for direction in directions:
                direction = direction.strip()
                if direction and len(direction) >= 3 and (direction, "研究方向") not in entities:
                    entities.append((direction, "研究方向"))

    # 6. 课程名称
    course_patterns = [
        r"主讲[《\s]*([^》，。；：]{3,20})[》]*课",
        r"《([^》]{3,20})》"
    ]
    for pattern in course_patterns:
        course_matches = re.findall(pattern, full_text)
        for course in course_matches:
            course = course.strip()
            if course and len(course) >= 3 and (course, "课程名称") not in entities:
                entities.append((course, "课程名称"))

    # 7. 毕业院校
    school_patterns = [
        r"毕业于([^，。；：\(\)（）]{4,20}[大学学院研究院])",
        r"获[硕博]士学位于([^，。；：\(\)（）]{4,20}[大学学院])"
    ]
    for pattern in school_patterns:
        school_matches = re.findall(pattern, full_text)
        for school in school_matches:
            school = school.strip()
            if school and any(x in school for x in ["大学", "学院", "研究院"]) and (school, "毕业院校") not in entities:
                entities.append((school, "毕业院校"))

    # 8. 荣誉称号
    honor_patterns = [
        r"获得([^，。；：\(\)（）]{4,30}称号)",
        r"入选([^，。；：\(\)（）]{4,30}计划)",
        r"([^，。；：\(\)（）]{4,30}人才)"
    ]
    for pattern in honor_patterns:
        honor_matches = re.findall(pattern, full_text)
        for honor in honor_matches:
            honor = honor.strip()
            if honor and len(honor) >= 4 and (honor, "荣誉称号") not in entities:
                entities.append((honor, "荣誉称号"))

    return entities


# -------------------------- 2. LLM自我纠错的三元组生成 --------------------------
def generate_relations_with_llm_correction(entities, text, teacher_name):
    """
    (已优化) 直接根据提取的实体全量生成三元组。
    第一步的LLM实体提取已经足够智能，第二步的LLM筛选反而会导致信息丢失（Over-filtering）。
    因此这里直接使用规则将所有提取出的实体转化为三元组。
    """
    entity_dict = defaultdict(list)
    for ent, typ in entities:
        if ent and typ in CONFIG["entity_types"]:
            entity_dict[typ].append(ent)

    if not entity_dict.get("教师姓名"):
        return []

    # 直接使用全量规则生成，保留所有提取到的信息
    return generate_triples_by_rules(entity_dict, teacher_name)


# -------------------------- 3. 规则引擎备份 --------------------------
def generate_triples_by_rules(entity_dict, teacher_name):
    """使用规则引擎替代Ollama，确保生成基础三元组"""
    triples = []
    # 按关系映射生成三元组
    for relation, entity_type in CONFIG["relation_mapping"].items():
        if entity_type in entity_dict and entity_dict[entity_type]:
            # 遍历所有有效实体，不再只取第一个
            for entity_value in entity_dict[entity_type]:
                triples.append((teacher_name, relation, entity_value))
    return triples


# -------------------------- 4. Excel读取 --------------------------
def read_teacher_excel(excel_path):
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Excel读取失败：{str(e)}")

    excel_columns = df.columns.tolist()
    print(f"Excel识别到的列名：{excel_columns}")

    # 定位姓名和个人介绍列
    name_col = next((col for col in excel_columns if any(key in str(col) for key in ["姓名", "导师姓名"])), None)
    intro_col = next((col for col in excel_columns if any(key in str(col) for key in ["个人介绍", "详细介绍", "简介", "详细内容"])),
                     None)
    if not name_col or not intro_col:
        raise ValueError(f"无法识别Excel列名。检测到的列名: {excel_columns}。请确保包含 '姓名' 和 '详细内容'/'个人介绍' 列。")

    # 生成结构化文本
    structured_texts = []
    df = df.fillna("")
    for idx, row in df.iterrows():
        teacher_name = str(row[name_col]).strip().replace(" ", "").replace("　", "")
        personal_intro = str(row[intro_col]).strip()
        if not teacher_name:
            print(f"第{idx + 1}行无姓名，跳过")
            continue
        full_text = f"导师姓名：{teacher_name}；个人介绍：{personal_intro[:CONFIG['max_text_length']]}"
        full_text = re.sub(r"\d{4}年|\d月生|男|女|邮箱：.*?[，。]", "", full_text)
        structured_texts.append({
            "index": idx + 1,
            "teacher_name": teacher_name,
            "full_text": full_text
        })
        print(f"第{idx + 1}行：姓名={teacher_name}，文本长度={len(full_text)}字")

    print(f"\nExcel处理完成：共{len(df)}行数据，生成{len(structured_texts)}条有效文本")
    return structured_texts


# -------------------------- 5. Neo4j操作 --------------------------
class Neo4jGraphManager:
    def __init__(self, uri=CONFIG["neo4j_uri"], username=CONFIG["neo4j_username"], password=CONFIG["neo4j_password"]):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            print("Neo4j连接成功（可视化地址：http://localhost:7474）")
        except exceptions.AuthError:
            raise ValueError("Neo4j用户名/密码错误")
        except exceptions.ServiceUnavailable:
            raise ConnectionError("Neo4j服务未启动")
        except Exception as e:
            raise Exception(f"Neo4j初始化失败：{str(e)}")

    def close(self):
        if self.driver:
            self.driver.close()
            print("🔌 Neo4j连接已关闭")

    def check_entity_exists(self, name):
        """检查实体是否已存在"""
        with self.driver.session() as session:
            result = session.run("MATCH (n:Entity {name: $name}) RETURN count(n) as count", name=name)
            return result.single()["count"] > 0

    def create_triple(self, head, relation, tail):
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (h:Entity {name: $head})
                    ON CREATE SET h.type = 'entity'
                    MERGE (t:Entity {name: $tail})
                    ON CREATE SET t.type = 'entity'
                    MERGE (h)-[r:RELATION {type: $relation}]->(t)
                    RETURN h, r, t
                """, head=head, relation=relation, tail=tail)
            
            # Sync to Django SQLite
            if Entity and Relationship:
                try:
                    # 获取或创建源实体
                    # 简单判断类型：如果是教师名字（在某个上下文里知道），类型设为person，否则一般设为entity
                    # 这里 reg5.py 主要是三元组，丢失了类型信息上下文，我们默认设为 unknown 或 entity
                    # 如果能判断 head 是 教师名，则为 person
                    
                    src_obj, _ = Entity.objects.get_or_create(
                        name=head, 
                        defaults={'entity_type': 'organization' if '学院' in head or '大学' in head else 'person' if len(head) < 4 else 'event'}
                    )
                    target_obj, _ = Entity.objects.get_or_create(
                        name=tail,
                        defaults={'entity_type': 'organization' if '学院' in tail or '大学' in tail else 'event'}
                    )
                    
                    # 简单的关系映射
                    rel_type_map = {
                        '属于': 'belongs_to',
                        '位于': 'located_in',
                        '参与': 'participated_in',
                        '任职': 'belongs_to',
                        '毕业于': 'related_to'
                    }
                    django_rel_type = rel_type_map.get(relation, 'related_to')
                    
                    Relationship.objects.get_or_create(
                        source_entity=src_obj,
                        target_entity=target_obj,
                        relationship_type=django_rel_type,
                        defaults={'description': relation}
                    )
                    # print(f"  [SQLite] Synced: {head} -> {tail}")
                except Exception as db_e:
                    print(f"  [SQLite] Sync failed: {db_e}")

            print(f"插入三元组：({head}, {relation}, {tail})")
        except Exception as e:
            print(f"插入失败：({head}, {relation}, {tail})，错误：{str(e)[:50]}")

    def batch_create_triples(self, triples):
        if not triples:
            print("️无有效三元组可导入")
            return
        print(f"\n=== 批量导入{len(triples)}个三元组 ===")
        for triple in triples:
            self.create_triple(*triple)
        print(f"=== 导入完成 ===")


# -------------------------- 主流程 --------------------------
def main():

    # 确定Excel路径
    if len(sys.argv) > 1:
        CONFIG["excel_path"] = sys.argv[1]
    else:
        current_dir = os.getcwd()
        # 排除临时文件（以 ~$ 开头）
        excel_files = [f for f in os.listdir(current_dir) 
                      if f.endswith((".xlsx", ".xls")) 
                      and "导师" in f 
                      and not f.startswith("~$")]
        if excel_files:
            CONFIG["excel_path"] = os.path.join(current_dir, excel_files[0])
            print(f"自动找到Excel文件：{CONFIG['excel_path']}")
        else:
            print("未找到导师Excel文件")
            return

    # 步骤1：读取Excel
    print("\n读取Excel数据")
    try:
        structured_teachers = read_teacher_excel(CONFIG["excel_path"])
    except Exception as e:
        print(f"失败：{str(e)}")
        return

    # 步骤1.5：过滤已存在的导师
    print("\n检查数据库中已存在的导师...")
    try:
        neo4j_manager = Neo4jGraphManager()
        new_teachers = []
        skipped_count = 0
        
        for teacher in structured_teachers:
            if neo4j_manager.check_entity_exists(teacher["teacher_name"]):
                print(f"  [跳过] {teacher['teacher_name']} (数据库已存在)")
                skipped_count += 1
            else:
                new_teachers.append(teacher)
        
        structured_teachers = new_teachers
        print(f"\n筛选结果：共 {len(structured_teachers) + skipped_count} 条，跳过 {skipped_count} 条，待处理 {len(structured_teachers)} 条")
        
        if not structured_teachers:
            print("没有新数据需要处理。")
            neo4j_manager.close()
            return

    except Exception as e:
        print(f"连接Neo4j检查失败，将全部处理：{e}")
        # 如果检查失败，不中断，继续全部处理（只是会多花点时间）

    # 步骤2：提取实体（LLM增强）
    print("\n批量提取实体（LLM增强）")
    all_entities = []
    for teacher in structured_teachers:
        print(f"\n处理第{teacher['index']}位导师：{teacher['teacher_name']}")
        entities = llm_enhance_entities(teacher["teacher_name"], teacher["full_text"])
        print(f"提取实体：{entities}")
        if entities:
            all_entities.append({
                "teacher_name": teacher["teacher_name"],
                "full_text": teacher["full_text"],
                "entities": entities
            })
    if not all_entities:
        print("未提取到实体，终止")
        return

    # 步骤3：生成三元组（LLM纠错）
    print("\n批量生成三元组（LLM纠错）")
    all_triples = []
    for teacher in all_entities:
        print(f"\n处理导师：{teacher['teacher_name']}")
        triples = generate_relations_with_llm_correction(
            teacher["entities"], teacher["full_text"], teacher["teacher_name"]
        )
        if triples:
            all_triples.extend(triples)
            print(f"🔗 有效三元组：{triples}")
        else:
            print(f"无有效三元组")

    # 三元组去重
    unique_triples = list(set(tuple(t) for t in all_triples))
    print(f"\n=== 三元组汇总 ===")
    print(f"原始数量：{len(all_triples)} | 去重后：{len(unique_triples)}")

    # 统计各关系类型数量
    relation_count = {}
    for triple in unique_triples:
        rel = triple[1]
        relation_count[rel] = relation_count.get(rel, 0) + 1
    print(f"关系类型统计：{relation_count}")

    # 步骤4：导入Neo4j
    print("\n导入Neo4j")
    try:
        # 复用上面已经创建的 neo4j_manager
        neo4j_manager.batch_create_triples(unique_triples)
        neo4j_manager.close()
    except Exception as e:
        print(f"步骤4失败：{str(e)}")
        return

    print(f"访问 http://localhost:7474")
    print(f"执行查询：MATCH (h:Entity)-[r:RELATION]->(t:Entity) RETURN h, r, t LIMIT 50")


if __name__ == "__main__":
    # 检查Ollama服务
    try:
        ollama.list()
    except Exception as e:
        print(f"Ollama服务未启动，将使用规则引擎模式：{str(e)}")
    main()