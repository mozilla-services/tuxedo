from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponseForbidden
from django.shortcuts import (get_list_or_404, get_object_or_404, render)
from django.template import RequestContext

from .forms import DjangoUserForm
