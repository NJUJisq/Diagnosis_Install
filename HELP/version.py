from __future__ import print_function
import sys
import re

if sys.version_info >= (3, 0):
    from itertools import zip_longest as izip_longest
else:
    from itertools import izip_longest


class _Comparable(object):

    """Rich comparison operators based on __lt__ and __eq__."""

    __gt__ = lambda self, other: not self < other and not self == other
    __le__ = lambda self, other: self < other or self == other
    __ne__ = lambda self, other: not self == other
    __ge__ = lambda self, other: self > other or self == other


class VersionError(Exception):
    pass

VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""

_re = re.compile(
    r"^\s*" + VERSION_PATTERN + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)

class _Seq(_Comparable):

    """Sequence of identifies that could be compared according to semver."""

    def __init__(self, seq):
        self.seq = seq

    def __lt__(self, other):
        assert set([int, str]) >= set(map(type, self.seq))
        for s, o in izip_longest(self.seq, other.seq):
            assert not (s is None and o is None)
            if s is None or o is None:
                return bool(s is None)
            if type(s) is int and type(o) is int:
                if s < o:
                    return True
            elif type(s) is int or type(o) is int:
                return type(s) is int
            elif s != o:
                return s < o

    def __eq__(self, other):
        return self.seq == other.seq


def _try_int(s):
    assert type(s) is str
    try:
        return int(s)
    except ValueError:
        return s


def _make_group(g):
    return [] if g is None else list(map(_try_int, g[1:].split('.')))


def remove_invalid(ver):

    clean_ver = []
    ch_vers = ver.split('.')
    for chs in ch_vers:
        clean_chs = ''
        for ch in chs:
            if ch.isdigit() or ch in ['*','0']:   
                clean_chs += ch 
            else:
                break 
        
        clean_ver.append(clean_chs)    
    clean_ver = '.'.join(clean_ver)

    print(ver,clean_ver)
    
    return clean_ver

class Version(_Comparable):

    def __init__(self, version):
        version = version.strip().strip('"').strip("'").strip(',').strip('(').strip('.') 
        self.version = version.strip()
        match = _re.match(version)
        if not match:
            self.version = remove_invalid(version) 
            match = _re.match(self.version) 
        if not match:
            raise VersionError('invalid version %r' % version) 
            
        version_dict = match.groupdict()
        self.release = version_dict['release'].split('.') 
        self.pre_release = version_dict['pre']
        self.post = version_dict['post'] 
        self.dev = version_dict['dev'] 
        self.local = version_dict['local']
        

    def __str__(self):
        s = '.'.join(str(s) for s in self._mmp())
        if self.pre_release:
            s += '%s' % (self.pre_release)
        if self.post:
            s += '%s' % (self.post)
        return s

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__str__())

    def _mmp(self):  
        norm_ = []
        for i in self.release:
            norm_.append(int(i)) 
        return norm_ 

    def compare_releases(self,version_num1,version_num2): 
        if len(version_num2) > len(version_num1):
            for i in range(len(version_num2) > len(version_num1)):
                version_num1.append('0')
        if len(version_num1) > len(version_num2):
            for i in range(len(version_num1) > len(version_num2)):
                version_num2.append('0') 
    
        for i,j in zip(version_num1,version_num2):
            if int(i)==int(j):
                continue
            if int(i) < int(j):
                return True
            if int(i)>int(j):
                return False

        return 'equal'  
    
    
    def __lt__(self, other):
        self._assume_to_be_comparable(other)
        if self._mmp() == other._mmp():  #when releases are consistent
            if self.pre_release == other.pre_release:
                if self.post == other.post:
                    return False
                elif self.post and other.post:
                    return _Seq(self.post) < _Seq(other.post)
                elif self.post or other.post:
                    return bool(other.post)  
                assert not 'reachable'
            elif self.pre_release and other.pre_release:
                return _Seq(self.pre_release) < _Seq(other.pre_release)
            elif self.pre_release or other.pre_release:
                return bool(self.pre_release)
            assert not 'reachable'
        
        
        return self.compare_releases(self._mmp(),other._mmp()) == True

    def __eq__(self, other):
        self._assume_to_be_comparable(other)
        return all([self.compare_releases(self._mmp(),other._mmp()) == 'equal',
                    self.post == other.post,
                    self.pre_release == other.pre_release,self.dev == other.dev,self.local== other.local])

    def _assume_to_be_comparable(self, other):
        if not isinstance(other, Version):
            raise TypeError('cannot compare `%r` with `%r`' % (self, other))


# test

# print(Version('0.01') >= Version('0.1.0'))