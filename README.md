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
    trace ?

#### grape grape 是一个django的远程查看日志的工具  ####
    grape 可以用来查看服务端的日志文件中的实时内容.
    
    安装:
        git clone https://github.com/kagxin/grape.git
        cd grape
        python setup.py install
        安装完成

    基本用法：
        服务端开启服务
            python manage.py grape

        打开客户端：
            python -m grape.management.commands.grape_client host 8080 username password.
            python -m grape.management.commands.grape_client 47.94.110.192 8080 admin 1
            然后在命令行进行操作。
            Usage：
                ？   ：   查看支持的命令
                off  ：   关闭日志打印
                bye  ：   关闭客户端程序。
                trace ： 进行日志打印。 

            ```
                example：
                           trace   file
                            trace 后的参数，为setting中设置的handles中的对应handle，并在当前目录保存一份打印日志的副本。
                例子中有一个
                (grape)trace 
                file  off   
                (grape)trace file

                打印handle为file的所对应的日志文件中的日志。
            ```
#####  接下来要完成的任务 #####
        1、连接方式 TCP ----> TLS