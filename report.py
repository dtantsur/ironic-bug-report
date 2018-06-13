#!/usr/bin/env python3

import argparse
import sys

import requests


ROOT = "https://storyboard.openstack.org/api/v1"

# NOTE(etingof): keep this in-sync with https://storyboard.openstack.org/#!/board/83
IRONIC_TRIAGING_BOARD = 83
TRIAGED_BUGS_LIST = 349
UNTRIAGED_BUGS_LIST = 350
TRIAGED_RFES_LIST = 351
UNTRIAGED_RFES_LIST = 348


def get(path):
    url = "%s/%s" % (ROOT, path.lstrip('/'))
    result = requests.get(url)
    result.raise_for_status()
    return result.json()


def log(*items):
    print(*items, file=sys.stderr)


def find_worklist(board, list_id):
    for lane in board.get('lanes', ()):
        if lane.get('list_id') == list_id:
            items = lane['worklist']['items']
            break
    else:
        raise RuntimeError('Cannot find list %d in the board' % list_id)

    return [item['story'] for item in items if 'story' in item]


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    stats_parser = subparsers.add_parser('stats')
    stats_parser.set_defaults(func=stats)

    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        parser.print_usage()
        return 2

    return func()


def stats():
    log('Fetching stories from board', IRONIC_TRIAGING_BOARD)
    board = get('/boards/%d' % IRONIC_TRIAGING_BOARD)

    triaged_bugs = find_worklist(board, TRIAGED_BUGS_LIST)
    untriaged_bugs = find_worklist(board, UNTRIAGED_BUGS_LIST)
    triaged_rfes = find_worklist(board, TRIAGED_RFES_LIST)
    untriaged_rfes = find_worklist(board, UNTRIAGED_RFES_LIST)

    print('Total bugs: %d' % (len(triaged_bugs) + len(untriaged_bugs)))
    print(' of them untriaged: %d (%.1f%%)' % (
        len(untriaged_bugs),
        len(untriaged_bugs) * 100. / (len(triaged_bugs) + len(untriaged_bugs))))
    print('Total RFEs: %d' % (len(triaged_rfes) + len(untriaged_rfes)))
    print(' of them untriaged: %d (%.1f%%)' % (
        len(untriaged_rfes),
        len(untriaged_rfes) * 100. / (len(triaged_rfes) + len(untriaged_rfes))))

    return 0

if __name__ == '__main__':
    sys.exit(main())
