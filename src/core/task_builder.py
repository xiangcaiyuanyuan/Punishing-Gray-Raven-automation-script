class TaskBuilder:
    """任务构建器，提供便捷的任务创建方法"""

    @staticmethod
    def click(image, clicks=1, interval=1):
        return {'type': 'click', 'image': image, 'clicks': clicks, 'interval': interval}

    @staticmethod
    def key_press(key, press_times=1, interval=1):
        return {'type': 'key_press', 'key': key, 'press_times': press_times, 'interval': interval}

    @staticmethod
    def offset_click(image, clicks=1, offset_x=0, offset_y=0):
        return {
            'type': 'offset_click',
            'image': image,
            'clicks': clicks,
            'offset_x': offset_x,
            'offset_y': offset_y
        }

    @staticmethod
    def move(actions):
        return {'type': 'move', 'actions': actions}

    @staticmethod
    def choice(*options):
        return {'type': 'choice', 'options': list(options)}

    @staticmethod
    def combo(*tasks):
        return {'type': 'combo', 'tasks': list(tasks)}

    @staticmethod
    def scroll(amount, image=None):
        task = {'type': 'scroll', 'amount': amount}
        if image:
            task['image'] = image
        return task

    @staticmethod
    def check(image, success_task, fail_task=None):
        images = image if isinstance(image, list) else [image]

        return {
            'type': 'check',
            'images': images,
            'success': success_task,
            'fail': fail_task
        }

    @staticmethod
    def wait(image=None, timeout=30, interval=0.5, fail_on_timeout=True):
        return {
            'type': 'wait',
            'image': image,
            'timeout': timeout,
            'interval': interval,
            'fail_on_timeout': fail_on_timeout
        }

    @staticmethod
    def reset_menu():
        """创建一个通用的返回主菜单任务块"""
        return {'type': 'reset_menu'}

    @staticmethod
    def loop(task):
        """创建循环任务，会一直重复执行直到用户中断"""
        return {'type': 'loop', 'task': task}

    @staticmethod
    def key_press_until_image(key, target_image, interval=0.5):
        """持续按键直到目标图片出现后停止"""
        return {
            'type': 'key_press_until_image',
            'key': key,
            'target_image': target_image,
            'interval': interval
        }


def create_claim_task():
    """创建每日任务领取流程"""
    return TaskBuilder.combo(
        TaskBuilder.choice(
            TaskBuilder.click('任务'),
            TaskBuilder.click('任务_1')
        ),
        TaskBuilder.choice(TaskBuilder.click('每日')),
        TaskBuilder.check(
            image='领取',
            success_task=TaskBuilder.combo(
                TaskBuilder.click('领取'),
                TaskBuilder.wait('活跃'),
                TaskBuilder.key_press('esc')
            ),
            fail_task=None
        )
    )


def claim_weekly_rewards():
    """创建每周任务领取流程"""
    return TaskBuilder.combo(
        TaskBuilder.click('任务_1'),
        TaskBuilder.choice(TaskBuilder.click('每周'),),
        TaskBuilder.choice(TaskBuilder.click('领取')),
        TaskBuilder.choice(TaskBuilder.click('补签卡')),
        TaskBuilder.key_press('esc')
    )

def create_team_setup_logic(team_image, key_char, scroll_back_amount):
    """【通用】配队流程：导航 -> 检查/新建 -> 应用"""
    return TaskBuilder.combo(
        TaskBuilder.click('准备'),
        TaskBuilder.click('预设'),
        TaskBuilder.offset_click('预设_1', 1, 0, 100),
        TaskBuilder.scroll(-3000),
        TaskBuilder.check(
            image=team_image,
            success_task=TaskBuilder.combo(
                TaskBuilder.click(team_image),
                TaskBuilder.click('使用')
            ),
            fail_task=TaskBuilder.combo(
                TaskBuilder.click('新增'),
                TaskBuilder.click('命名'),
                TaskBuilder.click('输入'),
                TaskBuilder.key_press(key_char, 8),
                TaskBuilder.key_press('enter'),
                TaskBuilder.click('确定_2'),
                TaskBuilder.click('选择'),
                TaskBuilder.click('参数', 1),
                TaskBuilder.scroll(-15000),
                TaskBuilder.scroll(scroll_back_amount),
                TaskBuilder.click('参数'),
                TaskBuilder.click('编入'),
                TaskBuilder.click('使用')
            )
        )
    )

