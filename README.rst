Ironic bug reporting
====================

Pulls and reports bug count from OpenStack Storyboard [1].

Requires:

* Python 3
* `requests <https://pypi.org/project/requests/>`_

Usage::

    $ ./report.py stats
    Fetching stories from board 67
    Total bugs: 285
     of them untriaged: 26
    Total RFEs: 246
     of them untriaged: 16

1. https://storyboard.openstack.org/#!/board/83