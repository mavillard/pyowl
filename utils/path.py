# -*- coding: utf-8 -*-
import re


class PathInfo:
    path_format = '^(.*/)?(\w+)(\.\w+)?$'
    
    def __init__(self, path):
        self._path = path
        pattern = re.compile(self.path_format)
        result = pattern.match(self._path)
        if result:
            groups = result.groups()
            self._filedir = groups[0]
            self._filename_noext = groups[1]
            self._filename = '%s%s' % (groups[1], groups[2])
        
    def get_filename_noext(self):
        return self._filename_noext
