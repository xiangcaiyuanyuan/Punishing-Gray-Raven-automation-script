from KyrieAuto.src.core.task_builder import TaskBuilder


def create_guitu():
    tasks=[
        TaskBuilder.reset_menu(),
        TaskBuilder.click('归途'),
        TaskBuilder.click('复制'),
        TaskBuilder.key_press('esc'),
        TaskBuilder.key_press('enter'),
        TaskBuilder.offset_click('频道', offset_y=50),
        TaskBuilder.choice(TaskBuilder.click('回归')),
        TaskBuilder.click('确定_2'),
        TaskBuilder.key_press('enter'),
        TaskBuilder.loop(
            TaskBuilder.combo(
                TaskBuilder.key_press(['ctrl', 'v']),
                TaskBuilder.key_press('enter'),
                TaskBuilder.key_press('enter'),
            )
        )
    ]
    return tasks

GUITU_TASKS = create_guitu()