"""
    矿区流程：
"""
from KyrieAuto.src.core.task_builder import TaskBuilder


def create_diggings_task():
    def one_time_process(index):
        return TaskBuilder.combo(
            TaskBuilder.click(f'矿区_{index}'),
            TaskBuilder.click('直达'),
            TaskBuilder.check(
                image='扫荡',
                success_task=TaskBuilder.combo(
                    TaskBuilder.click('扫荡'),
                    TaskBuilder.click('返回'),
                    TaskBuilder.key_press('esc')
                ),
                fail_task=TaskBuilder.key_press('esc',2)
            )
        )

    tasks = [
        TaskBuilder.reset_menu(),
        TaskBuilder.click('战斗'),
        TaskBuilder.click('挑战'),
        TaskBuilder.click('矿区'),
        *[one_time_process(index) for index in range(1,4)],
        TaskBuilder.scroll(100),
        one_time_process(index=4),
        TaskBuilder.click('奖励'),
        TaskBuilder.choice(TaskBuilder.click('领取')),
        TaskBuilder.reset_menu()
    ]
    return tasks


KUANGQU_TASKS = create_diggings_task()