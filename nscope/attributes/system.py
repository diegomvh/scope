#!/usr/bin/env python

import platform

def attributes(scope, file_path = None, project_directory = None):
    return scope.push_scope("attr.os-version." + platform.release())
