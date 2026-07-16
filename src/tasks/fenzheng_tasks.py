"""
    纷争战区流程：
"""
from KyrieAuto.src.core.task_builder import TaskBuilder, create_team_setup_logic, claim_weekly_rewards


def create_fenzheng_tasks():

    def one_time_process(index):
        task =TaskBuilder.combo(
                TaskBuilder.click(f'zhanqu_{index}'),
                TaskBuilder.click('准备'),
                create_team_setup_logic(FENZHENG_CONFIGS[index]['team_img'], FENZHENG_CONFIGS[index]['key'],
                                        FENZHENG_CONFIGS[index]['scroll_back']),
                TaskBuilder.click('开始'),
                TaskBuilder.wait('退出', 60, 10),
                TaskBuilder.click('退出', 2, 5),
            )
        return task


    tasks = [
        TaskBuilder.reset_menu(),
        TaskBuilder.click('战斗'),
        TaskBuilder.click('挑战'),
        TaskBuilder.click('纷争'),
        *[one_time_process(index) for index in range(1,3)],
        TaskBuilder.reset_menu(),
        claim_weekly_rewards(),
        TaskBuilder.reset_menu()
    ]
    return tasks


# 纷争战区配置列表
FENZHENG_CONFIGS = [
    {
        'name': '队伍1',
        'team_img': '队伍_1',
        'key': 'k',
        'scroll_back': 0
    },
    {
        'name': '队伍2',
        'team_img': '队伍_2',
        'key': 'y',
        'scroll_back': 150
    },
    {
        'name': '队伍3',
        'team_img': '队伍_3',
        'key': 'e',
        'scroll_back': 300
    }
]


FENZHENG_TASKS = create_fenzheng_tasks()

