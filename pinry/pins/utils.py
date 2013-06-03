#utilites related to pins
import operator
from urlparse import urlparse, urlunparse 
from django.http import Http404 

from django.db.models import Count
from django.conf import settings

from django.contrib.auth.models import User
from .models import Pin
from follow.models import Follow
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site

current_site = Site.objects.get_current()
root_url = "http://%s" % unicode(current_site)

def get_top_domains(srcUrls, qty=1):
    '''
    Return top domains in list:
    srcUrl format: [(srcUrl,count)]
    '''
    srcDomains = {}
    for url in srcUrls:
        p = urlparse(url[0])
        dom = p.netloc or unicode(current_site.domain)
        if dom in current_site.domain or dom in settings.MEDIA_URL:
            dom = "Uploaded"
        count = url[1]
        parts = p.scheme, p.netloc, '', '', '', ''
        url = urlunparse(parts)
        if dom not in srcDomains and dom != '':
            srcDomains[dom] = count, url
        elif dom != '':
            srcDomains[dom] = srcDomains[dom][0]+count, url

    srcDomains = sorted(srcDomains.iteritems(), key=operator.itemgetter(1), reverse=True)
    return srcDomains[:qty]
    
    
def getProfileContext(profileId):
    '''not used: keep for reference
    from django.core.serializers.json import DjangoJSONEncoder
    authUser = User.objects.values('id','username','first_name','last_name','date_joined','last_login').filter(username__exact=request.user)
    authUserJ = simplejson.dumps(list(authUser), cls = DjangoJSONEncoder)
    '''
    try:
        profile = User.objects.get(id__exact=profileId)
    except:
        raise Http404  
    pins = Pin.objects.filter(submitter=profile)
    pinsC = pins.count()
    tags = pins.order_by('tags__name').filter(submitter=profile).values_list('tags__name').annotate(count=Count('tags__name'))
    tagsC = tags.distinct().count()
    followers = Follow.objects.get_follows(profile)
    followersC = followers.count()
    followersL = followers.values_list('user__username', flat=True)
    following = Follow.objects.filter(user=profile).exclude(folowing__exact=None)
    followingL = following.values_list('folowing__username', flat=True)
    followingC = followingL.count()
    #TODO: get folowing pins
    favs = Follow.objects.filter(user=profile).exclude(favorite__exact=None).values_list('favorite__pk', flat=True)
    favsC = favs.count()
    cmnts = Comment.objects.filter(user=profile, content_type__name = 'pin', site_id=settings.SITE_ID ).values_list('pk', flat=True)
    cmntsC = cmnts.count()

    
    #create dictionary of srcUrls striped to domain > convert to sorted list > put top 5 in srcDoms
    srcUrls = pins.order_by('srcUrl').values_list('srcUrl').annotate(count=Count('srcUrl'))
    srcDoms = get_top_domains(srcUrls, 5)
    ''' DEBUG
    print pinsC
    print tags
    print tagsC
    print folowers
    print folowersC
    print folowing
    print folowingC
    print favs
    print favsC
    print srcDoms
    print cmnts
    print cmntsC
    '''
    context = {
            'profile': profile,
            'pinsC': pinsC,
            'followers': followers,
            'followersC': followersC,
            'following': following,
            'followingC': followingC,
            'tags': tags,
            'tagsC': tagsC,
            'favs': favs,
            'favsC': favsC,
            'cmnts': cmnts,
            'cmntsC': cmntsC,
            'srcDoms': srcDoms,
            #'authUser': authUser,
            #'authUserJ': authUserJ
        }
    return context
    
def getPinContext(request, pinId):
    try:
        pin = Pin.objects.get(id=pinId)
    except:
        raise Http404  
    #datetime, favorite, folowing, id, user
    pin.favorites = Follow.objects.filter(favorite__id=pin.id)
    pin.favoritesC = pin.favorites.count()
    #comments are obtained in template
    #pin.comments = Comment.objects.for_model(Pin).filter(object_pk=pin.id)
    #pin.cmntsC = pin.comments.count()
    pin.tags = pin.tags.all()
    pin.tagsC = pin.tags.count()
    pin.repins = Pin.objects.filter(repin=pin)
    pin.repinsC = pin.repins.count()
    pin.srcDom = get_top_domains([(pin.srcUrl,1)], 1)[0][0]
    
    next = Pin.objects.filter(id__gt=pinId)
    prev = Pin.objects.filter(id__lt=pinId)
    if next:
        pin.next = next.order_by('id')[:1][0].id
    else:
        pin.next = prev.order_by('id')[:1][0].id
    if prev:
        pin.prev = prev.order_by('-id')[:1][0].id
    else:
        pin.prev = next.order_by('-id')[:1][0].id

    user = request.user
    user.fav = False
    for fav in pin.favorites:
        if fav.user == user:
            user.fav = True
    user.repin = False
    for repin in pin.repins:
        if repin.submitter == user:
            user.repin = True
    user.cmnt = False
    
    user.pin = False
    if pin.submitter == user:
        user.pin = True

    '''
    print pin
    print pin.favorites
    print pin.favoritesC
    #print pin.comments
    #print pin.cmntsC
    print pin.tags
    print pin.tagsC
    print pin.repins
    print pin.repinsC
    
    print user.fav
    print user.repin
    print user.cmnt
    print user.pin
    '''

    context = {
            'pin': pin,
            'user': user,
        }
    return context

'''
 Determines if user is friends with test_user:
 If you already have a query set for the user's followers and following then
 you may include them to prevent another query.
'''    
def get_relationships(user, following=None, followers=None):
    friends = []
    if not followers and not following:
        followers = Follow.objects.get_follows(user)
        following = Follow.objects.filter(user=user).exclude(folowing__exact=None)
    followersL = [follow.user for follow in followers]
    followingL = [follow.folowing for follow in following]
    for follow in following:
        if follow.folowing in followersL:
            friends.append(follow.folowing)
            followersL.remove(follow.folowing)
            followingL.remove(follow.folowing)
    '''
    friendsL = [user for user in friends]
    followers_f = followers.exclude(user__in=friendsL)
    following_f = following.exclude(folowing__in=friendsL)
    '''
    return {'friends':friends, 'followers':followersL, 'following':followingL}

