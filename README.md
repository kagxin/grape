##### Welcome to the grape.  A remote logging tool for django. #####

#### IF ####

``` python

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

    python -m grape_client host port username password

    example:
        python -m grape_client 127.0.0.1 8080 admin 1

    trace handlers
    trace file
    trace off


