# -*- coding: utf-8 -*-
import re


class PathInfo(object):
    path_format = '^(.*/)?(\w+)(\.\w+)?$'
    
    def __init__(self, path):
        self._path = path
        pattern = re.compile(self.path_format)
        match = pattern.match(self._path)
        if match:
            groups = match.groups()
            self._filedir = groups[0]
            self._filename_noext = groups[1]
            self._extension = groups[2]
            self._filename = '{0}{1}'.format(
                self._filename_noext,
                self._extension
            )
        
    def get_filename_noext(self):
        return self._filename_noext
