#!/usr/bin/env python

import os
from glob import glob

BUILD_RULES = [
    { "attribute": 'attr.project.make',  "glob": 'Makefile',    "group": 'build', },
    { "attribute": 'attr.project.rake',  "glob": 'Rakefile',    "group": 'build', },
    { "attribute": 'attr.project.xcode', "glob": '*.xcodeproj', "group": 'build', },
    { "attribute": 'attr.project.ninja', "glob": '*.ninja',     "group": 'build', },
    { "attribute": 'attr.project.lein',  "glob": '*.lein',      "group": 'build', },
]

def attributes(scope, file_path = None, project_directory = None):
    source =  os.path.split(file_path)[0] if file_path is not None else project_directory
    if source:
        while True:
            for rule in BUILD_RULES:
                pattern = os.path.join(source, rule["glob"])
                if glob(pattern):
                    scope.push_scope(rule["attribute"])
                    break
            source, tail = os.path.split(source)
            if not tail:
                break
