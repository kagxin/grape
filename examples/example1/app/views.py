from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
import logging
import time
# Create your views here.

logger = logging.getLogger('django.request')

class TestView(View):
    def get(self, *args, **kwargs):
        while True:
            logger.error('for test error log')
            time.sleep(1)
        return HttpResponse('test')
