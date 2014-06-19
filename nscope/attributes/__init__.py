#!/usr/bin/env python

from .system import attributes as system_attributes
from .scm import attributes as scm_attributes
from .path import attributes as path_attributes
from .build import attributes as build_attributes

def attributes(scope, file_path = None, project_directory = None):
    for function in (path_attributes, system_attributes, scm_attributes, build_attributes):
        function(scope, file_path, project_directory)