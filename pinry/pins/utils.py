#utilites related to pins

from urlparse import urlparse, urlunparse 
def get_top_domains(srcUrls, qty):
    srcDomains = {}
    for url in srcUrls:
        p = urlparse(url[0])
        dom = p.netloc
        count = url[1]
        parts = p.scheme, p.netloc, '', '', '', ''
        url = urlunparse(parts)
        if dom not in srcDomains and dom != '':
            srcDomains[dom] = count, url
        elif dom != '':
            srcDomains[dom] = srcDomains[dom][0]+count, url
    print srcDomains
    import operator
    srcDomains = sorted(srcDomains.iteritems(), key=operator.itemgetter(1), reverse=True)
    return srcDomains[:qty]