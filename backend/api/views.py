from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from services.ai_service import AIService

# AI助手相关视图函数
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ask_ai_assistant(request):
    """AI助手问答接口"""
    try:
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response({'error': '问题不能为空'}, status=400)
            
        answer = AIService.ask(question)
        return Response({'answer': answer})
            
    except Exception as e:
        return Response({'answer': f'系统错误: {str(e)}'}, status=500)

