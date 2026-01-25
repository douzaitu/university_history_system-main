import os
import pandas as pd
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from knowledge_graph.models import Entity

class Command(BaseCommand):
    help = '导入导师信息Excel数据 - 标点符号修复版'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Excel文件路径')

    def fix_punctuation(self, text):
        """专门修复标点符号问题"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text)
        
        # 只修复特定的标点问题，不影响其他内容
        # 修复邮箱地址
        text = re.sub(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+)\.([a-zA-Z0-9-.]+)', 
                     lambda m: f"{m.group(1)}@{m.group(2)}.{m.group(3)}", text)
        
        # 修复URL
        text = re.sub(r'(https?://[^\s。]+)\.([^\s。]+)\.([^\s。]+)', 
                     lambda m: f"{m.group(1)}.{m.group(2)}.{m.group(3)}", text)
        
        # 修复常见的网站域名
        domains = ['com', 'cn', 'org', 'net', 'edu', 'gov', 'io', 'github']
        for domain in domains:
            text = re.sub(f'{domain}\。', f'{domain}.', text)
        
        return text

    def extract_images_from_excel(self, file_path):
        """从Excel中提取图片"""
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(file_path)
            worksheet = workbook.active
            
            images = {}
            for img in worksheet._images:
                row = img.anchor._from.row + 1
                col = img.anchor._from.col + 1
                
                if row not in images:
                    images[row] = {}
                images[row][col] = img
            
            return images, worksheet
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'提取图片时出错: {str(e)}'))
            return {}, None

    def save_image(self, image, teacher_name, row_num):
        """保存图片到媒体目录"""
        try:
            image_dir = os.path.join(settings.MEDIA_ROOT, 'teacher_photos')
            os.makedirs(image_dir, exist_ok=True)
            
            if teacher_name and teacher_name.strip() and teacher_name not in ['未知', '补充中']:
                safe_name = "".join(c for c in teacher_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}.png"
            else:
                filename = f"teacher_{row_num}.png"
            
            image_path = os.path.join(image_dir, filename)
            
            with open(image_path, 'wb') as f:
                f.write(image._data())
            
            return f'teacher_photos/{filename}'
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'保存图片失败 {teacher_name}: {str(e)}'))
            return ''

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'文件不存在: {file_path}'))
            return

        try:
            # 提取图片
            self.stdout.write('正在提取Excel中的图片...')
            images_dict, worksheet = self.extract_images_from_excel(file_path)
            
            # 读取数据 - 使用openpyxl引擎，避免自动转换
            self.stdout.write('正在读取Excel数据...')
            df = pd.read_excel(file_path, engine='openpyxl')
            
            created_count = 0
            updated_count = 0
            image_count = 0
            
            for index, row in df.iterrows():
                excel_row_num = index + 2
                
                if pd.isna(row['姓名']) or row['姓名'] in ['未知', '补充中']:
                    continue
                
                teacher_name = str(row['姓名']).strip()
                
                # 获取原始数据
                description = str(row['简介']) if not pd.isna(row['简介']) else ''
                detailed_content = str(row['详细内容']) if not pd.isna(row['详细内容']) else ''
                
                # 调试输出
                self.stdout.write(f"处理 {teacher_name}...")
                if '@' in description or '@' in detailed_content:
                    self.stdout.write(f"  发现邮箱地址，进行修复")
                
                # 只修复标点符号问题
                description = self.fix_punctuation(description)
                detailed_content = self.fix_punctuation(detailed_content)
                
                full_description = f"{description}\n\n{detailed_content}".strip()
                
                # 处理图片
                photo_url = ''
                if excel_row_num in images_dict and 1 in images_dict[excel_row_num]:
                    image = images_dict[excel_row_num][1]
                    photo_url = self.save_image(image, teacher_name, excel_row_num)
                    if photo_url:
                        image_count += 1
                
                # 创建或更新实体
                entity, created = Entity.objects.update_or_create(
                    name=teacher_name,
                    entity_type='person',
                    defaults={
                        'description': full_description,
                        'photo_url': photo_url
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'创建实体: {entity.name}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'更新实体: {entity.name}'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'导入完成！创建: {created_count}, 更新: {updated_count}, 图片: {image_count}, 总计: {created_count + updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入失败: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())