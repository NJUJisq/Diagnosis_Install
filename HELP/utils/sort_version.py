
# import re
# PEP440_VERSION_RE = re.compile(r'^v?(\d+!)?(\d+(\.\d+)*)((a|b|c|rc)(\d+))?'
#                                r'(\.(post)(\d+))?(\.(dev)(\d+))?'
#                                r'(\+([a-zA-Z\d]+(\.[a-zA-Z\d]+)?))?$')

def cmp_version(v1,v2):  # #
   
    if v1 == 'False' or v2 == 'False':
        return -1
    from version import Version
    v1 = Version(v1)
    v2 = Version(v2)
    if v1 > v2:
        return 1
    if v1 == v2:
        return 0
    return -1
    

def cmp_version_reverse(v1,v2): 

    if v1 == 'False' or v2 == 'False':
        return 1
    from version import Version
    v1 = Version(v1)
    v2 = Version(v2)
    if v1 > v2:
        return -1
    if v1 == v2:
        return 0
    return 1

# test
# l = ['3.4.11.45','3.4.13.47','3.4.14.51','3.4.15.55','3.4.16.59','4.4.0.46','4.5.1.48','4.5.2.52','4.5.3.56','4.5.4.58','4.5.4.60']
# l.sort(key=functools.cmp_to_key(cmp_version))
# print(l)
# print('end')
