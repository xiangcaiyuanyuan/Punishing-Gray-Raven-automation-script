from KyrieAuto.src.core.task_builder import *
def create_juzhen_tasks():
    tasks = [
        TaskBuilder.reset_menu(),
        TaskBuilder.click('战斗'),
        TaskBuilder.click('挑战'),
        TaskBuilder.click('漫纪'),
        TaskBuilder.click('演绎'),
        TaskBuilder.click('矩阵'),
        TaskBuilder.loop(
            TaskBuilder.combo(
                TaskBuilder.choice(
                    TaskBuilder.click('启程_1'),
                    TaskBuilder.click('启程_2')
                ),
                TaskBuilder.click('下一步'),
                TaskBuilder.check(
                    image='能量',
                    success_task=TaskBuilder.combo(
                        TaskBuilder.click('能量'),
                        TaskBuilder.click('下一步'),
                    )
                ),
                TaskBuilder.click('加号_2'),
                TaskBuilder.click('编入_2'),
                TaskBuilder.click('演算'),
                TaskBuilder.click('摇曳'),
                TaskBuilder.click('搭档'),
                TaskBuilder.click('确定_3'),
                TaskBuilder.click('选择_1'),
                TaskBuilder.click('决定'),
                TaskBuilder.click('出发',2),
                TaskBuilder.click('攻击'),
                TaskBuilder.click('确定_3'),
                TaskBuilder.click('出击'),
                TaskBuilder.key_press_until_image('=', '领取_2', interval=0.5),
                TaskBuilder.key_press('esc'),
                TaskBuilder.click('确认'),
                TaskBuilder.click('终止'),
                TaskBuilder.click('确认', 2),
                TaskBuilder.click('下一页', 4,0.1),
            )
        )
    ]
    return tasks


JUZHEN_TASKS = create_juzhen_tasks()