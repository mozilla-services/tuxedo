import os

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


def _get_command_list():
    templates = os.listdir(os.path.join(os.path.dirname(__file__), 'templates',
                                        'docs'))
    # cut out the command names only
    commands = [ t[:-5] for t in templates if t.endswith('.html') ]
    commands.sort()
    return commands

def docindex(request):
    """API Doc Index"""
    data = {'commands': _get_command_list()}
    return render_to_response('index.html', data, context_instance=
                              RequestContext(request))

def docs(request, command):
    """Individual API docs"""
    if command not in _get_command_list():
        raise Http404
    return render_to_response('docs/%s.html' % command, context_instance=
                              RequestContext(request))

