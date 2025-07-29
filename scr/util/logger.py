import logging
import os

import colorlog
from scr.PATH import heart_log


class Logger:
    _instance = None  # 单例实例

    def __new__(cls):
        # 实现单例模式
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # 创建 Logger
        self.logger = logging.getLogger("HeartLogger")  # 使用唯一名称
        self.logger.setLevel(logging.DEBUG)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建控制台 Handler
            console_handler = logging.StreamHandler()

            # 配置颜色格式
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)s | %(message)s",
                datefmt='%Y-%m-%d %H:%M',
                log_colors={
                    'DEBUG': 'white',  # 白色
                    'INFO': 'white',  # 白色
                    'WARNING': 'yellow',  # 黄色（默认警告色）
                    'ERROR': 'red',  # 红色
                    'CRITICAL': 'red,bg_white'  # 红字白底
                }
            )

            if not os.path.exists(heart_log):
                os.makedirs(heart_log)
            file_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            file_handler = logging.FileHandler(f"{heart_log}\\heart.log", encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # 记录所有级别到文件
            file_handler.setFormatter(file_formatter)

            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        else:
            # 如果处理器已存在，只需更新日志级别
            self.logger.setLevel(logging.DEBUG)

    def debug(self, msg: object):
        self.logger.debug(msg)

    def info(self, msg: object):
        self.logger.info(msg)

    def warning(self, msg: object):
        self.logger.warning(msg)

    def error(self, msg: object):
        self.logger.error(msg)

    def critical(self, msg: object):
        self.logger.critical(msg)