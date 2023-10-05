import logging # 引入logging模块

formatter = '%(asctime)s - %(funcName)s - %(filename)s - %(levelname)s - %(message)s' #定义了一个formatter,用于格式化日志信息

# get_logger function,用于记录日志
def get_logger(logger_name):
    logger = logging.getLogger(logger_name) # 创建一个logger对象
    logger.setLevel(logging.DEBUG)          # 设置logger的level为DEBUG

    # create console handler and set level to debug
    console_handler = logging.StreamHandler()  # 创建一个console handler
    console_handler.setLevel(logging.DEBUG)    # 设置console handler的level为DEBUG
    ch_format = logging.Formatter(formatter)   # 设置console handler的格式
    console_handler.setFormatter(ch_format)    

    logger.addHandler(console_handler)        # 将console handler添加到logger中

    return logger                             # 返回logger
