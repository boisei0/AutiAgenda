__author__ = 'Rob Derksen (boisei0)'


# taken from http://stackoverflow.com/a/1695250/1930315
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse'] = reverse
    return type('Enum', (), enums)