import os.path

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


DOCFILES = os.path.join(os.path.dirname(__file__), 'docs', '%s.md')

def _get_doc(command):
    """
    get the markdown doc for an API command.
    Throws IOError if not found.
    """
    doc = open(DOCFILES % command, 'r')
    return doc.read()

def docs(request, command):
    """
    API docs
    For simplicity, API docs are Markdown files with a path pattern of
    DOCFILES.
    """
    try:
        data = {'doctext': _get_doc(command)}
    except IOError:
        raise Http404
    return render_to_response('docs.html', data, context_instance=
                              RequestContext(request))

