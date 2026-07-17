"""
日志系统 - 统一管理所有日志输出
"""
import logging
import sys
import os
from datetime import datetime

# ── 终端颜色 ──
COLOR_MAP = {
    'DEBUG': '\033[36m',      # 青色
    'INFO': '\033[32m',       # 绿色
    'WARNING': '\033[33m',    # 黄色
    'ERROR': '\033[31m',      # 红色
    'RESET': '\033[0m',       # 重置
}


class ColoredFormatter(logging.Formatter):
    """终端彩色格式化"""

    def format(self, record):
        level = record.levelname
        color = COLOR_MAP.get(level, COLOR_MAP['RESET'])
        reset = COLOR_MAP['RESET']
        # 简短的终端格式：仅 [级别] 消息
        return f"{color}[{level}]{reset} {record.getMessage()}"


class FileFormatter(logging.Formatter):
    """文件日志详细格式化（含时间戳）"""

    def format(self, record):
        t = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{t}] [{record.levelname}] {record.getMessage()}"


def _get_log_dir():
    """获取日志文件存放目录（与 progress.json 同级）"""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'logs')


def setup_logger(name='Kyrie'):
    """配置并返回 logger 实例"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # ── 终端处理器（INFO 及以上显示彩色日志）──
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(ColoredFormatter())
    logger.addHandler(console)

    # ── 文件处理器（所有级别写入文件，含时间戳）──
    try:
        log_dir = _get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'kyrie_{datetime.now().strftime("%Y%m%d")}.log')
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(FileFormatter())
        logger.addHandler(fh)
    except Exception:
        pass  # 日志文件写入失败不影响运行

    return logger


# 全局单例
_logger = None


def get_logger():
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


# 便捷函数
def debug(msg):    get_logger().debug(msg)
def info(msg):     get_logger().info(msg)
def warning(msg):  get_logger().warning(msg)
def error(msg):    get_logger().error(msg)
