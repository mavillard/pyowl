# -*- coding: utf-8 -*-
import re
from xml.etree import ElementTree as ET

class Dictionary:
    def __init__(self, dictionary):
        self.dict = dictionary
    
    def reverse(self):
        d = {}
        for k, v in self.dict.items():
            d[v] = k
        return d


class ElementTreeWriter:
    def __init__(self, root, dst, encoding='utf-8', method='xml'):
        self.root = root
        self.dst = dst
        self.encod = encoding
        self.method = method
    
    def write(self, ns={}):
        file_dst = open(self.dst, "w")
        file_dst.write('%s\n' % XMLNSParser.xml_declaration)
        qnames, namespaces = ET._namespaces(self.root, self.encod, None)
        namespaces.update(Dictionary(ns).reverse())
        serialize = ET._serialize[self.method]
        serialize(file_dst.write, self.root, self.encod, qnames, namespaces)
        file_dst.close()



class PathInfo:
    path_format = '^(.*/)?(\w+)(\.\w+)?$'
    
    def __init__(self, path):
        self.path = path
        pattern = re.compile(self.path_format)
        result = pattern.match(self.path)
        if result:
            groups = result.groups()
            self.file_dir = groups[0]
            self.file_name_noext = groups[1]
            self.file_name = "%s%s" % (groups[0], groups[1])
        
    def get_file_name_noext(self):
        return self.file_name_noext


class XMLNSParser:
    xml_declaration = '<?xml version="1.0"?>'
    
    def __init__(self, source):
        self._ns = self._parse(source)
    
    def __repr__(self):
        return '%s' % self._ns
    
    def get_xmlns(self):
        return self._ns
    
    def get_xmlns_noprefix(self):
        ns = {}
        for k in self._ns.keys():
            i = k.find(':') 
            if i != -1:
                ns[k[i+1:]] = self._ns[k]
            else:
                ns[''] = self._ns[k]
        return ns
    
    def _parse(self, source):
        ns = {}
        string = ''
        stack = []
        finish = False
        f = open(source)
        for line in f:
            if finish:
                break
            for char in line:
                if finish:
                    break
                if stack == ['x']:
                    if string.startswith('rdf:RDF', 1):
                        ns = self._process_ns(string)
                        finish = True
                    else:
                        stack.pop()
                        string = ''
                else:
                    self._process_stack(stack, char)
                    if stack:
                        string = '%s%s' % (string, char)
        f.close()
        return ns
    
    def _process_stack(self, stack, char):
        if char == '<':
            if not stack:
                stack.append('x')
            stack.append(char)
        elif char == '>':
            if stack[-1] == '<':
                stack.pop()
            else:
                stack.append(char)
    
    def _process_ns(self, string):
        ns = {}
        pattern = re.compile('\S+\s*=\s*"\S*"')
        matches = pattern.findall(string)
        for match in matches:
            tupl = match.split('=')
            name = tupl[0].rstrip()
            value = tupl[1].lstrip()[1:-1]
            ns[name] = value
        return ns
