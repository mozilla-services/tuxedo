from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from forms import DjangoUserForm, UserProfileForm


@login_required
def profile(request, user):
    data = {}

    if request.POST:
	django_user_form = DjangoUserForm(request.POST, instance=user)
        user_profile_form = UserProfileForm(request.POST,
					    instance=user.get_profile())

        if django_user_form.is_valid() and user_profile_form.is_valid():
            django_user_form.save()
            user_profile_form.save()
            data['success'] = True

    else:
	django_user_form = DjangoUserForm(instance=user)
	user_profile_form = UserProfileForm(instance=user.get_profile())

    data.update({
        'django_user_form': django_user_form,
        'user_profile_form': user_profile_form,
    })

    return render_to_response('registration/profile.html', data,
                              context_instance=RequestContext(request))


@login_required
def own_profile(request):
    return profile(request, request.user)


@permission_required('users.change_user')
def profile_edition(request, username):
    django_user = get_object_or_404(DjangoUser, username=username)
    if django_user.is_staff:
	return HttpResponseForbidden(u'You don\'t have the permission to edit this user')
    return profile(request, django_user)
