#!/usr/bin/env python3

import argparse
import itertools
import sys

import requests


ROOT = "https://storyboard.openstack.org/api/v1"
IRONIC_GROUP = 75
IRONIC_TRIAGING_BOARD = 67
UNTRIAGED_LIST = 284
NEW_RFES_LIST = 286


def get(path):
    url = "%s/%s" % (ROOT, path.lstrip('/'))
    result = requests.get(url)
    result.raise_for_status()
    return result.json()


def log(*items):
    print(*items, file=sys.stderr)


def is_bug(story):
    assert 'tags' in story, list(story)
    return (story.get('is_bug', True) and 'rfe' not in story['tags'] and
            'rfe-approved' not in story['tags'])


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
    log('Fetching stories from group', IRONIC_GROUP)
    stories = get('/stories?project_group_id=%d&status=active' % IRONIC_GROUP)
    log('Fetching stories from board', IRONIC_TRIAGING_BOARD)
    board = get('/boards/%d' % IRONIC_TRIAGING_BOARD)

    bugs = list(filter(is_bug, stories))
    untriaged = list(filter(is_bug, find_worklist(board, UNTRIAGED_LIST)))
    print('Total bugs:', len(bugs))
    print(' of them untriaged:', len(untriaged))

    rfes = list(itertools.filterfalse(is_bug, stories))
    new_rfes = find_worklist(board, NEW_RFES_LIST)
    print('Total RFEs:', len(rfes))
    print(' of them untriaged:', len(new_rfes))


if __name__ == '__main__':
    sys.exit(main())
