import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from services.ai_service import AIService

try:
    print("Testing AIService.ask('测试')...")
    result = AIService.ask("测试")
    print("\nResult:")
    print(result)
except Exception as e:
    import traceback
    print("\nException occurred:")
    traceback.print_exc()
