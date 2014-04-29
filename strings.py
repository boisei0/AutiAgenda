import gettext
import locale

__author__ = 'Rob Derksen (boisei0)'


# start ignoring translations required at runtime
def _(text):
    return text


class TextData:
    def __init__(self):
        pass

    months = {
        1: _('January'),
        2: _('February'),
        3: _('March'),
        4: _('April'),
        5: _('May'),
        6: _('June'),
        7: _('Juli'),
        8: _('August'),
        9: _('September'),
        10: _('October'),
        11: _('November'),
        12: _('December')
    }

    weekdays_abbr = {
        1: _('Mo'),
        2: _('Tu'),
        3: _('We'),
        4: _('Th'),
        5: _('Fr'),
        6: _('Sa'),
        7: _('Su')
    }

    about = {
        'title': _('About...'),
        'text': _('{0} was made by {1} for the Kivy App Contest 2014.')
    }

    courses_dialog = {
        'name_title': _('Name'),
        'name_descr': _('Name of the course'),
        'abbr_title': _('Abbreviation'),
        'abbr_descr': _('Abbreviation of the course'),
        'col_title': _('Colour'),
        'col_descr': _('Colour of the course'),
        'active_title': _('Active'),
        'active_descr': _('Is the course active')
    }

    date_name = {
        'yesterday': _('Yesterday'),
        'today': _('Today'),
        'tomorrow': _('Tomorrow')
    }

    text = {
        'homework': 'homework',
        'schedule': 'schedule',
        'courses': 'courses',
        'sync': 'synchronize',
        'agenda': 'personal organizer',
        'settings': 'settings',
        'close': 'close'
    }


# end ignoring translations
del _


def get_locale():
    if locale.getdefaultlocale()[0] is not None:
        return locale.getdefaultlocale()[0][0:2]
    else:
        return 'en'