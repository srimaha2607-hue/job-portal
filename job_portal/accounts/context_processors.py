def user_role_processor(request):
    ctx = {'is_admin': False, 'is_recruiter': False, 'is_seeker': False}
    if request.user.is_authenticated:
        ctx['is_admin'] = request.user.is_admin
        ctx['is_recruiter'] = request.user.is_recruiter
        ctx['is_seeker'] = request.user.is_seeker
    return ctx
