# myapp/context_processors.py

def following_count(request):
    if request.user.is_authenticated:
        return {'following_count': request.user.following_count()}
    return {'following_count': 0}
