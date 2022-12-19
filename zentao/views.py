from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class BugView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('hello, getn')

    # def post(self, request, *args, **kwargs):
    #     return HttpResponse('hello, postn')
    #
    # def put(self, request, *args, **kwargs):
    #     return HttpResponse('hello, putn')
    #
    # def delete(self, request, *args, **kwargs):
    #     return HttpResponse('hello, deleten')
    #
    # @csrf_exempt
    # def dispatch(self, request, *args, **kwargs):
    #     return super(TestView, self).dispatch(request, *args, **kwargs)
