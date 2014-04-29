import pstats

__author__ = 'Rob Derksen (boisei0)'


def parse_profile(filename):
    parser = pstats.Stats(filename)
    parser.print_stats()

if __name__ == '__main__':
    parse_profile('/home/boisei0/.config/agenda/AutiAgenda.profile')