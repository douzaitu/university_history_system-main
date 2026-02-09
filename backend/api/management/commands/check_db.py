import os
from django.core.management.base import BaseCommand
from django.conf import settings
from neo4j import GraphDatabase

class Command(BaseCommand):
    help = '检查数据库连接状态 (SQLite 和 Neo4j)'

    def handle(self, *args, **options):
        self.stdout.write("=== 校史系统数据库连接检查 ===\n")
        
        # 1. Check SQLite
        self.check_sqlite()
        
        # 2. Check Neo4j
        self.check_neo4j()

    def check_sqlite(self):
        self.stdout.write("[1/2] 检查 Django 默认数据库 (SQLite)...")
        db_path = settings.DATABASES['default']['NAME']
        
        if os.path.exists(db_path):
            size_kb = os.path.getsize(db_path) / 1024
            self.stdout.write(self.style.SUCCESS(f"✅ SQLite 数据库文件存在: {db_path}"))
            self.stdout.write(f"   大小: {size_kb:.2f} KB")
        else:
            self.stdout.write(self.style.ERROR(f"❌ SQLite 数据库文件未找到: {db_path}"))
            self.stdout.write("   Django 可能还未运行迁移 (python manage.py migrate)")

    def check_neo4j(self):
        self.stdout.write("\n[2/2] 检查 Neo4j 图数据库连接...")
        
        # 获取配置，优先使用环境变量，否则使用默认值
        uri = os.getenv('NEO4J_URI', "bolt://localhost:7687")
        user = os.getenv('NEO4J_USERNAME', "neo4j")
        password = os.getenv('NEO4J_PASSWORD', "12345678")
        
        self.stdout.write(f"   尝试连接到: {uri} (用户: {user})")
        
        driver = None
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            self.stdout.write(self.style.SUCCESS("✅ Neo4j 连接成功!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Neo4j 连接失败: {str(e)}"))
            self.stdout.write("   请确保 Neo4j 服务正在运行且端口 7687 开放。")
        finally:
            if driver:
                driver.close()
