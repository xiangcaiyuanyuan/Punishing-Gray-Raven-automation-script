from KyrieAuto.src.core.task_builder import TaskBuilder
def create_hanjing():
    task = [
        TaskBuilder.reset_menu(),
        TaskBuilder.click('战斗'),
        TaskBuilder.click('挑战'),
        TaskBuilder.click('漫纪'),
        TaskBuilder.click('演绎'),
        TaskBuilder.click('寒境'),
        TaskBuilder.click('启程'),
        TaskBuilder.check(
            image='严霜',
            success_task=TaskBuilder.click('下一步_1'),
            fail_task=TaskBuilder.combo(
                TaskBuilder.check(
                    image='严霜_1',
                    success_task=TaskBuilder.combo(
                        TaskBuilder.click('严霜_1'),
                        TaskBuilder.click('下一步_1'),
                    ),
                    fail_task=TaskBuilder.combo(
                        TaskBuilder.choice(
                            TaskBuilder.scroll(2000, 'C'),
                            TaskBuilder.scroll(2000, 'C_1')
                        ),
                        TaskBuilder.scroll(-1500),
                        TaskBuilder.click('下一步_1'),
                        TaskBuilder.click('启动资金'),
                        TaskBuilder.click('确定_5'),
                        TaskBuilder.click('招募',2),
                        TaskBuilder.wait(5),
                        TaskBuilder.key_press('esc'),
                    )
                )
            )
        )
    ]
    return task


HANJING_TASKS = create_hanjing()
