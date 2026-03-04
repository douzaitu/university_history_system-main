import os
import pandas as pd
import re
import traceback
from collections import defaultdict
from django.conf import settings
from django.utils import timezone
from knowledge_graph.models import Entity, Relationship
from services.llm_bridge import LLMBridge
from .models import Document

def process_document_task(document_id):
    """
    后台任务入口：处理文档（通常运行在独立线程中）
    """
    try:
        # 重新从数据库获取最新状态
        document = Document.objects.get(id=document_id)
        print(f"Start processing document: {document.title} (ID: {document.id})")
    except Document.DoesNotExist:
        return

    try:
        # 执行核心处理逻辑
        result = DocumentProcessor.process(document)
        
        # 更新成功状态
        document.status = 'processed'
        document.processed_data = result
    except Exception as e:
        # 更新失败状态
        error_msg = f"{str(e)}"
        print(f"Processing failed: {error_msg}")
        traceback.print_exc()
        
        document.status = 'error'
        document.processed_data = {
            "error": error_msg,
            "traceback": traceback.format_exc()[-500:] # 只保留最后一部分堆栈
        }
    finally:
        document.processing_end_time = timezone.now()
        document.save()

class DocumentProcessor:
    CONFIG = {
        "max_text_length": 2500,
        "entity_types": [
            "教师姓名", "院系", "职称", "研究方向", "课程名称", "毕业院校", "荣誉称号", "工作职责"
        ],
        "relation_mapping": {
            "属于": "院系",
            "拥有": "职称",
            "研究": "研究方向",
            "主讲": "课程名称",
            "毕业于": "毕业院校",
            "获得": "荣誉称号",
            "负责": "工作职责"
        }
    }

    @classmethod
    def process(cls, document):
        """主处理逻辑"""
        file_path = document.file.path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. 尝试提取 Excel 中的图片
        images_map = cls._extract_images_from_excel(file_path)

        # 2. 读取 Excel 文本
        texts = cls._read_excel(file_path)
        if not texts:
            raise ValueError("无法从Excel中提取有效文本，请检查列名是否包含'姓名'和'介绍'")

        processed_count = 0
        triples_count = 0
        
        # 3. 逐行处理
        for item in texts:
            teacher_name = item['teacher_name']
            full_text = item['full_text']
            intro = item.get('intro', '')
            excel_row = item['excel_row_index']

            # A. 更新/创建 人物实体 (SQLite -> Signal -> Neo4j)
            update_defaults = {
                'entity_type': 'person',  
                'description': intro      
            }
            
            # 如果这行有对应的图片，保存并更新
            if excel_row in images_map:
                try:
                    photo_url = cls.save_excel_image(images_map[excel_row], teacher_name, excel_row)
                    if photo_url:
                        update_defaults['photo_url'] = photo_url
                except Exception as e:
                    print(f"Image save failed for {teacher_name}: {e}")
            
            Entity.objects.update_or_create(
                name=teacher_name,
                defaults=update_defaults
            )

            # B. 使用 LLM 提取实体和关系
            # 只有当简介不为空时才进行提取
            if len(full_text) > 10:
                entities = LLMBridge.extract_entities(full_text, teacher_name, cls.CONFIG['entity_types'])
                triples = cls._generate_triples(entities, teacher_name)
                
                # C. 保存生成的三元组
                for head, relation, tail in triples:
                    cls._save_triple(head, relation, tail)
                    triples_count += 1
            
            processed_count += 1

        return {
            "status": "success",
            "processed_count": processed_count,
            "triples_count": triples_count,
            "message": f"成功处理 {processed_count} 位导师数据，生成 {triples_count} 条关系。"
        }

    @classmethod
    def _extract_images_from_excel(cls, file_path):
        """提取Excel中的图片映射 {row_index: image_obj}"""
        images_map = {}
        try:
            from openpyxl import load_workbook
            wb = load_workbook(file_path)
            ws = wb.active
            for img in getattr(ws, '_images', []):
                # openpyxl row从0开始计数(旧版)或从1开始(新版)，需要根据版本确认
                # 通常 anchor._from.row 是 0-indexed 的，所以行号 = value + 1
                row_idx = img.anchor._from.row + 1
                col_idx = img.anchor._from.col + 1
                # 假设图片在第1列
                if col_idx == 1:
                    images_map[row_idx] = img
        except Exception as e:
            print(f"Warning: Could not extract images from excel: {e}")
        return images_map

    @classmethod
    def save_excel_image(cls, image, teacher_name, row_num):
        """保存Excel中的图片到媒体目录"""
        try:
            image_dir = os.path.join(settings.MEDIA_ROOT, 'teacher_photos')
            os.makedirs(image_dir, exist_ok=True)
            
            # 生成安全的文件名
            if teacher_name and teacher_name.strip():
                safe_name = re.sub(r'[^\w\s-]', '', teacher_name).strip()
                filename = f"{safe_name}.png"
            else:
                filename = f"teacher_row_{row_num}.png"
            
            image_path = os.path.join(image_dir, filename)
            
            with open(image_path, 'wb') as f:
                f.write(image._data())
            
            return f'teacher_photos/{filename}'
        except Exception as e:
            print(f"Save image error: {e}")
            return ""

    @classmethod
    def _read_excel(cls, file_path):
        """读取Excel文件内容"""
        try:
            # 优先使用 pandas 读取数据
            df = pd.read_excel(file_path)
            
            # 模糊匹配列名
            columns = [str(c) for c in df.columns]
            name_col = next((c for c in columns if any(k in c for k in ["姓名", "导师姓名"])), None)
            intro_col = next((c for c in columns if any(k in c for k in ["个人介绍", "详细介绍", "简介", "基本情况", "详细内容", "介绍"])), None)
            
            if not name_col or not intro_col:
                print(f"Excel columns missing required fields. Found: {columns}")
                return []

            results = []
            df = df.fillna("")
            for idx, row in df.iterrows():
                name = str(row[name_col]).strip().replace(" ", "")
                intro = str(row[intro_col]).strip()
                
                if not name or name == "nan":
                    continue
                    
                full_text = f"导师姓名：{name}；个人介绍：{intro[:cls.CONFIG['max_text_length']]}"
                # 简单清洗
                full_text = re.sub(r"\d{4}年|\d月生|男|女|邮箱：.*?[，。]", "", full_text)
                
                results.append({
                    "teacher_name": name,
                    "full_text": full_text,
                    "intro": intro,
                    "excel_row_index": idx + 2 # Header is row 1
                })
            return results
        except Exception as e:
            print(f"Read Excel error: {e}")
            raise e

    @classmethod
    def _generate_triples(cls, entity_dict, teacher_name):
        """生成三元组"""
        triples = []
        mapping = cls.CONFIG["relation_mapping"]
        
        for relation, ent_type in mapping.items():
            if ent_type in entity_dict:
                for val in entity_dict[ent_type]:
                    val = str(val).strip()
                    if val and val != teacher_name:
                        triples.append((teacher_name, relation, val))
        return triples

    @classmethod
    def _save_triple(cls, head, relation, tail):
        """保存三元组 (Auto-synced to Neo4j via Signals)"""
        try:
            src, _ = Entity.objects.get_or_create(
                name=head, 
                defaults={'entity_type': 'person'}
            )
            
            # Simple Entity Type Inference
            tgt_type = 'event' # Default fallback
            tail_lower = tail.lower()
            
            if any(k in tail_lower for k in ['大学', '学院', '系', '所', '中心', '实验室', '委员会', '学会']):
                tgt_type = 'organization'
            elif any(k in tail_lower for k in ['省', '市', '区', '路', '街', 'building', '室']):
                tgt_type = 'location'
            elif relation in ['主讲', '研究']:
               tgt_type = 'subject'

            tgt, _ = Entity.objects.get_or_create(
                name=tail, 
                defaults={'entity_type': tgt_type}
            )
            
            # 修改逻辑：只要源和目标相同，就更新关系类型，而不是新建
            # 注意：这会导致覆盖旧的关系。例如如果原关系是"属于"，新关系是"任教于"，则"属于"会被覆盖。
            Relationship.objects.update_or_create(
                source_entity=src,
                target_entity=tgt,
                defaults={'relationship_type': relation}
            )
        except Exception as e:
            print(f"Save triple error: {e}")
