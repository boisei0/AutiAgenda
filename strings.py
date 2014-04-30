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
        7: _('July'),
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
        'title': _('About...'),  # as in: about the program
        'text': _('{0} was made by {1} for the Kivy App Contest 2014.')  # {0} as in name of the program, {1} as in name of the author
    }

    courses_dialog = {
        'name_title': _('Name'),
        'name_descr': _('Name of the course'),  # course as in: subject, 'study material'
        'abbr_title': _('Abbreviation'),
        'abbr_descr': _('Abbreviation of the course'),  # course as in: subject, 'study material'
        'col_title': _('Colour'),
        'col_descr': _('Colour of the course'),  # course as in: subject, 'study material'
        'active_title': _('Active'),
        'active_descr': _('Is the course active')  # course as in: subject, 'study material'
    }

    date_name = {
        'yesterday': _('Yesterday'),
        'today': _('Today'),
        'tomorrow': _('Tomorrow')
    }

    text = {
        'homework': _('homework'),
        'schedule': _('schedule'),  # as in: time schedule
        'courses': _('courses'),  # course as in: subject, 'study material'
        'sync': _('synchronise'),
        'agenda': _('personal organizer'),
        'settings': _('settings'),  # as in: software settings
        'close': _('close'),  # as in: to close
        'lesson': _('lesson')
    }


# end ignoring translations
del _


def get_locale():
    if locale.getdefaultlocale()[0] is not None:
        return locale.getdefaultlocale()[0][0:2]
    else:
        return 'en'