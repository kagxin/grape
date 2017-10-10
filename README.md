##### Welcome to the grape.  A remote logging tool for django. #####

#### IF ####

``` python

django 
setting.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### THEN ####

    Usage:
        python manage.py grape
        python -m grape.management.commands.grape_client host port username password.

    example:
            python -m grape.management.commands.grape_client 127.0.0.1 8080 admin 1

    trace handlers
    trace file
    trace off

#### grape grape 是一个django的远程查看日志的工具 ####

