from server.settings.base import DATETIME_FORMAT

def strdatime(datime):
    return datime.strftime(DATETIME_FORMAT)
