from django.http import HttpResponse
from django.shortcuts import render_to_response

def index(request):
    """Main login/index page"""
    return HttpResponse('OMG')

def uptake(request):
    """Show mirror uptake"""
    return HttpResponse('OMG')

