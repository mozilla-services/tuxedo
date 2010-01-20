from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import DjangoUserForm, UserProfileForm


@login_required
def profile(request):
    data = {}

    if request.POST:
        django_user_form = DjangoUserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST,
                                            instance=request.user.get_profile())

        if django_user_form.is_valid() and user_profile_form.is_valid():
            django_user_form.save()
            user_profile_form.save()
            data['success'] = True

    else:
        django_user_form = DjangoUserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=request.user.get_profile())

    data.update({
        'django_user_form': django_user_form,
        'user_profile_form': user_profile_form,
    })

    return render_to_response('registration/profile.html', data,
                              context_instance=RequestContext(request))

