#!/usr/bin/env python

import os

def attributes(scope, file_path = None, project_directory = None):
    if file_path:
        rev_path = file_path.replace(" ", "_").split(os.sep)
        if not rev_path[0]:
            rev_path.pop(0)
        rev_path = rev_path[:-1] + rev_path[-1].split(".") + ['rev-path', 'attr']
        scope.push_scope(".".join(rev_path[::-1]))
    else:
        scope.push_scope('attr.untitled')
