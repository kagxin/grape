from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
import logging
# Create your views here.

logger = logging.getLogger('django.request')

class TestView(View):
    def get(self, *args, **kwargs):
        logger.error('for test error log')
        return HttpResponse('test')
