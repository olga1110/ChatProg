# Настройку логгера выполнить в отдельном модуле log_config.py:
# Создание именованного логгера.
# Сообщения лога должны иметь следующий формат:
# "<дата-время> <уровеньважности> <имямодуля> <имя_функции> <сообщение>"
# Журналирование должно производиться в лог-файл.
# На стороне сервера необходимо настроить ежедневную ротацию лог-файлов


import logging
import logging.handlers


# logger = None
# log_client = None


def log_serv_init():

    # global logger
    logger = logging.getLogger("server_messanger_log")
    logger_file_name = 'server_messanger_log.log'
    fn = logging.handlers.TimedRotatingFileHandler(logger_file_name, when='D',
                                            interval=1,
                                            backupCount=31)

    fn.setLevel(logging.DEBUG)
    # file_error_handler = logging.handlers.TimedRotatingFileHandler("error_messanger.log", when="M",
    #                                         interval=1,
    #                                         backupCount=31)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    fn.setFormatter(formatter)

    logger.addHandler(fn)
    logger.setLevel(logging.DEBUG)
    return logger


# logger.addHandler(file_error_handler)
# file_error_handler.setFormatter(formatter)
# file_error_handler.setLevel(logging.ERROR)

def log_client_init():

    # global log_client
    log_client = logging.getLogger("client_messanger_log")
    log_cl_file_name = 'client_messanger_log.log'

    fn_client = logging.handlers.TimedRotatingFileHandler(log_cl_file_name, when='D',
                                            interval=1,
                                            backupCount=31)

    fn_client.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    fn_client.setFormatter(formatter)
    log_client.addHandler(fn_client)
    log_client.setLevel(logging.DEBUG)
    return log_client




