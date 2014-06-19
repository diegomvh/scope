#!/usr/bin/env python

import os
from glob import glob

SCM_RULES = [
    { "attribute": 'attr.scm.svn',       "glob": '.svn',        "group": 'scm',   },
    { "attribute": 'attr.scm.hg',        "glob": '.hg',         "group": 'scm',   },
    { "attribute": 'attr.scm.git',       "glob": '.git',        "group": 'scm',   },
    { "attribute": 'attr.scm.p4',        "glob": '.p4config',   "group": 'scm',   },
]

def attributes(scope, file_path = None, project_directory = None):
    source = os.path.split(file_path)[0] if file_path is not None else project_directory
    if source:
        while True:
            for rule in SCM_RULES:
                pattern = os.path.join(source, rule["glob"])
                if glob(pattern):
                    scope.push_scope(rule["attribute"])
                    break
            source, tail = os.path.split(source)
            if not tail:
                break