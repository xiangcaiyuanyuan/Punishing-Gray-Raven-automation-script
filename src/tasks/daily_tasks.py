"""
    日常任务流程：
"""
from KyrieAuto.src.core.task_builder import TaskBuilder, create_claim_task


def create_daily_tasks():
    # 日常任务序列
    tasks = [
        TaskBuilder.reset_menu(),
        # --- 公会签到 ---
        TaskBuilder.choice(TaskBuilder.click('图标')),
        TaskBuilder.click('公会'),
        TaskBuilder.check(
            image='推荐',
            success_task=TaskBuilder.key_press('esc'),
            fail_task=TaskBuilder.combo(
                TaskBuilder.choice(TaskBuilder.click('关闭')),
                TaskBuilder.move([
                    ('公会_1', 0, 0, 1.5, 0),
                    ('公会_2', 1.5, 1, 0, 0),
                    ('公会_3', 0, 0, 1, 0.5),
                    ('公会_4', 0, 0, 1.5, 0.25),
                    ('公会_5', 0, 1.5, 1.25, 0),
                    ('公会_6', 0, 0, 1.2, 0),
                    ('公会_7', 0, 1.7, 2, 0),
                ]),
                TaskBuilder.check(
                    image='查看',
                    success_task=TaskBuilder.key_press('esc'),
                    fail_task=TaskBuilder.check(
                        image='签到',
                        success_task=TaskBuilder.combo(
                            TaskBuilder.click('签到'),
                            TaskBuilder.key_press('esc',2)
                        ),
                        fail_task=TaskBuilder.combo(
                            TaskBuilder.key_press('esc'),
                            TaskBuilder.check(
                                image='签到',
                                success_task=TaskBuilder.combo(
                                    TaskBuilder.click('签到'),
                                    TaskBuilder.key_press('esc',2)
                                ),
                                fail_task=None
                            )
                        )
                    )
                ),
            )
        ),

        # --- 采购补给包 ---
        TaskBuilder.click('采购'),
        TaskBuilder.click('补给包'),
        TaskBuilder.click('日常补给'),
        TaskBuilder.check(
            image='限购',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('限购'),
                TaskBuilder.click('购买_1'),
                TaskBuilder.key_press('esc'),
            ),
            fail_task=None
        ),
        TaskBuilder.check(
            image='血清',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('血清'),
                TaskBuilder.click('购买_1'),
                TaskBuilder.key_press('esc',2),
            ),
            fail_task=TaskBuilder.key_press('esc')
        ),

        # --- 宿舍委托 ---
        TaskBuilder.click('宿舍'),
        TaskBuilder.choice(TaskBuilder.click('关闭')),
        TaskBuilder.click('委托'),
        TaskBuilder.choice(
            TaskBuilder.combo(
                TaskBuilder.click('归队'),
                TaskBuilder.key_press('esc', 1)
            )
        ),
        TaskBuilder.combo(
            TaskBuilder.click('派遣'),
            TaskBuilder.key_press('esc', 1)
        ),
        TaskBuilder.choice(
            TaskBuilder.combo(
                TaskBuilder.click('摸头'),
                TaskBuilder.key_press('esc', 1)
            )
        ),

        # --- 执勤 ---
        TaskBuilder.click('执勤'),
        TaskBuilder.choice(
            TaskBuilder.combo(
                TaskBuilder.click('执勤_完成'),
                TaskBuilder.key_press('esc')
            )
        ),

        TaskBuilder.check(
            image='加号_1',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('加号_1'),
                TaskBuilder.click('体力'),
                TaskBuilder.click('执勤_1'),
                TaskBuilder.key_press('esc')
            ),
            fail_task=TaskBuilder.key_press('esc', 1)
        ),

        # --- 宿舍任务 ---
        TaskBuilder.click('任务_宿舍'),
        TaskBuilder.check(
            image='领取',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('领取'),
                TaskBuilder.key_press('esc', 2)
            ),
            fail_task=TaskBuilder.key_press('esc', 1)
        ),

        # --- 商店购买 ---
        TaskBuilder.click('商店'),
        TaskBuilder.check(
            image='草稿',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('草稿'),
                TaskBuilder.click('购买'),
                TaskBuilder.key_press('esc', 2)),
            fail_task=TaskBuilder.key_press('esc', 2)
        ),

        # --- 任务领取 ---
        create_claim_task(),
        TaskBuilder.key_press('esc'),

        # --- 仓库道具 (血清) ---
        TaskBuilder.click('仓库'),
        TaskBuilder.choice(
            TaskBuilder.click('道具'),
            TaskBuilder.click('道具_1')),
        TaskBuilder.check(
            image='血清_1',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('血清_1'),
                TaskBuilder.click('加号', 3),
                TaskBuilder.click('使用'),
                TaskBuilder.key_press('esc', 1),
                TaskBuilder.check(
                    image='血清_1',
                    success_task=TaskBuilder.combo(
                        TaskBuilder.click('血清_1'),
                        TaskBuilder.click('加号', 3),
                        TaskBuilder.click('使用'),
                        TaskBuilder.key_press('esc', 2),
                    ),
                    fail_task=TaskBuilder.key_press('esc', 1)
                )
            ),
            fail_task=TaskBuilder.key_press('esc', 1)
        ),

        # --- 战斗资源 (拟战) ---
        TaskBuilder.click('战斗'),
        TaskBuilder.click('资源'),
        TaskBuilder.click('拟战'),
        TaskBuilder.check(
            image='自动_1',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('自动_1'),
                TaskBuilder.wait(timeout=5),
                TaskBuilder.check(
                    image='升级',
                    success_task=TaskBuilder.key_press('esc'),
                    fail_task=None
                ),
                TaskBuilder.click('确定'),
            ),
            fail_task=TaskBuilder.combo(
                TaskBuilder.click('多重挑战'),
                TaskBuilder.check(
                    image='参数_1',
                    success_task=None,
                    fail_task=TaskBuilder.combo(
                        TaskBuilder.click('预设'),
                        TaskBuilder.click('新增'),
                        TaskBuilder.click('选择'),
                        TaskBuilder.click('编入'),
                        TaskBuilder.click('使用'),
                    )
                ),
                TaskBuilder.click('开始'),
                TaskBuilder.key_press_until_image('=', '返回'),
                TaskBuilder.click('返回'),
            )#手动挑战设计
        ),
        TaskBuilder.key_press('esc', 2),

        # --- 最终领取 ---
        create_claim_task(),
        TaskBuilder.check(
            image='礼包',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('礼包'),
                TaskBuilder.key_press('esc', 2)
            ),
            fail_task=TaskBuilder.key_press('esc', 1)
        ),

        # --- BP奖励 ---
        TaskBuilder.choice(
            *[TaskBuilder.click(f'bp_{i}') for i in range(1, 20)] + [TaskBuilder.click('bp')]
        ),
        TaskBuilder.wait(['领取_1_tmp','领取_1','评定']),
        TaskBuilder.choice(
            TaskBuilder.click('确定_1')
        ),
        TaskBuilder.wait('评定'),
        TaskBuilder.click('评定'),
        TaskBuilder.choice(TaskBuilder.click('领取_1',2,2)),
        TaskBuilder.click('战略'),
        TaskBuilder.choice(TaskBuilder.click('领取_1')),
        TaskBuilder.reset_menu()
    ]
    return tasks


DAILY_TASKS = create_daily_tasks()