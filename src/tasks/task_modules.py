from KyrieAuto.src.tasks.daily_tasks import DAILY_TASKS
from KyrieAuto.src.tasks.huantong_tasks import HUANTONG_TASKS
from KyrieAuto.src.tasks.fenzheng_tasks import FENZHENG_TASKS
from KyrieAuto.src.tasks.guitu_tasks import GUITU_TASKS
from KyrieAuto.src.tasks.kuangqu_tasks import KUANGQU_TASKS
from KyrieAuto.src.tasks.juzhen_tasks import JUZHEN_TASKS
from KyrieAuto.src.tasks.hanjing_tasks import HANJING_TASKS

TASK_MODULES = {
    '日常任务': {'name': '日常任务', 'tasks': DAILY_TASKS},
    '幻痛囚笼': {'name': '幻痛囚笼', 'tasks': HUANTONG_TASKS},
    '纷争战区': {'name': '纷争战区', 'tasks': FENZHENG_TASKS},
    '矿区': {'name': '矿区', 'tasks': KUANGQU_TASKS},
    '矩阵循生':{'name': '矩阵循生', 'tasks': JUZHEN_TASKS},
    '寒境曙光':{'name': '寒境曙光', 'tasks': HANJING_TASKS},
    '归途之旅': {'name': '归途之旅', 'tasks': GUITU_TASKS},
}
