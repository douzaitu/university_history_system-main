from django.apps import AppConfig


class KnowledgeGraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge_graph'
    verbose_name = '知识图谱管理'

    def ready(self):
        import knowledge_graph.signals
        try:
            from django.apps import apps
            from django.utils.translation import gettext_lazy as _
            
            # 尝试汉化 Django Q 的显示名称
            django_q_app = apps.get_app_config('django_q')
            django_q_app.verbose_name = "任务队列管理"
            
            # 尝试汉化 Django Q 的模型名称
            Task = apps.get_model('django_q', 'Task')
            Task._meta.verbose_name = "任务"
            Task._meta.verbose_name_plural = "所有任务"

            Success = apps.get_model('django_q', 'Success')
            Success._meta.verbose_name = "成功任务"
            Success._meta.verbose_name_plural = "成功任务"

            Failure = apps.get_model('django_q', 'Failure')
            Failure._meta.verbose_name = "失败任务"
            Failure._meta.verbose_name_plural = "失败任务"

            Schedule = apps.get_model('django_q', 'Schedule')
            Schedule._meta.verbose_name = "定时任务"
            Schedule._meta.verbose_name_plural = "定时任务"
            
            OrmQ = apps.get_model('django_q', 'OrmQ')
            OrmQ._meta.verbose_name = "队列消息"
            OrmQ._meta.verbose_name_plural = "队列消息"

            # 汉化字段显示的通用函数
            def patch_fields(model, field_mapping):
                for field_name, verbose_name in field_mapping.items():
                    try:
                        model._meta.get_field(field_name).verbose_name = verbose_name
                    except:
                        pass
            
            # 任务记录字段汉化 (Success/Failure)
            task_field_map = {
                'name': '任务ID',
                'func': '执行函数',
                'group': '任务组',
                'started': '开始时间',
                'stopped': '结束时间',
                'result': '执行结果',
                'group': '分组',
                'time_taken': '耗时(秒)',
                'cluster': '执行集群',
                'args': '参数',
                'kwargs': '关键词参数',
                'attempt_count': '尝试次数'
            }
            patch_fields(Success, task_field_map)
            patch_fields(Failure, task_field_map)
            
            # 定时任务字段汉化
            schedule_field_map = {
                'name': '名称',
                'func': '执行函数',
                'hook': '回调函数',
                'args': '参数',
                'kwargs': '关键词参数',
                'schedule_type': '调度类型',
                'minutes': '分钟间隔',
                'repeats': '重复次数',
                'next_run': '下次运行时间',
                'cron': 'Cron表达式',
                'cluster': '执行集群'
            }
            patch_fields(Schedule, schedule_field_map)

            # 队列字段汉化
            ormq_field_map = {
                'key': '任务Key',
                'payload': '数据载荷',
                'lock': '锁定时间'
            }
            patch_fields(OrmQ, ormq_field_map)
            
        except Exception as e:
            pass

