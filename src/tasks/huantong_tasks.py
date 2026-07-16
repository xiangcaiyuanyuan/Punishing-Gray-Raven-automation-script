"""
    幻痛囚笼流程：
"""
from KyrieAuto.src.core.task_builder import TaskBuilder, create_team_setup_logic, claim_weekly_rewards


def create_group_sequence(group_config):
    """【总控】根据配置生成一整组（骑士+混沌+地狱）的流程"""
    group_offset = group_config['group_img']
    team_img = group_config['team_img']
    key = group_config['key']
    scroll_amt = group_config.get('scroll_back', 0)

    # 定义三个难度的图片名
    knight_imgs = '骑士'
    hundun_imgs = '混沌'
    diyu_imgs = '地狱'

    def create_difficulty_battle(imgs, team_image, key_char, scroll_back_amount):
        task = TaskBuilder.combo(
            TaskBuilder.choice(TaskBuilder.click(imgs)),
            TaskBuilder.check(
                image='自动',
                success_task=TaskBuilder.combo(
                    TaskBuilder.click('自动'),
                    TaskBuilder.click('执行'),
                ),
                fail_task=TaskBuilder.combo(
                    create_team_setup_logic(team_image, key_char, scroll_back_amount),
                    TaskBuilder.click('开始'),
                    TaskBuilder.wait('保存', timeout=60, interval=1),
                    TaskBuilder.click('保存')
                )
            )
        )
        return task

    tasks = TaskBuilder.combo(
        TaskBuilder.offset_click(group_offset, 1, 0, 300),
        create_difficulty_battle(knight_imgs, team_img, key, scroll_amt),
        create_difficulty_battle(hundun_imgs, team_img, key, scroll_amt),
        create_difficulty_battle(diyu_imgs, team_img, key, scroll_amt),
        TaskBuilder.key_press('esc')
    )

    return tasks


def create_huantong_tasks():
    """创建幻痛囚笼任务序列"""
    tasks = [
        TaskBuilder.reset_menu(),
        TaskBuilder.click('战斗'),
        TaskBuilder.click('挑战'),
        TaskBuilder.click('幻痛'),
        TaskBuilder.choice(
            TaskBuilder.combo(
                TaskBuilder.offset_click('终极',1,0,100),
                TaskBuilder.click('确定_2')
            )
        ),
        *[create_group_sequence(config) for config in GROUP_CONFIGS],
        TaskBuilder.key_press('esc', 2),
        claim_weekly_rewards(),
        TaskBuilder.reset_menu()
    ]

    return tasks


# 幻痛囚笼配置列表
GROUP_CONFIGS = [
    {
        'name': 'A组',
        'group_img': 'A组',
        'team_img': '队伍_1',
        'key': 'k',
        'scroll_back': 0
    },
    {
        'name': 'B组',
        'group_img': 'B组',
        'team_img': '队伍_2',
        'key': 'y',
        'scroll_back': 150
    },
    {
        'name': 'C组',
        'group_img': 'C组',
        'team_img': '队伍_3',
        'key': 'e',
        'scroll_back': 300
    }
]


HUANTONG_TASKS = create_huantong_tasks()