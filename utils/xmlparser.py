# -*- coding: utf-8 -*-
import re
from xml.etree import ElementTree as ET

from dictionary import Dictionary


class ElementTreeWriter(ET.ElementTree):
    def __init__(self, root, dst, encoding='utf-8', method='xml'):
        self._root = root
        self._dst = dst
        self._encod = encoding
        self._method = method
    
    def write(self, ns={}):
        file_dst = open(self._dst, "w")
        file_dst.write('{0}\n'.format(XMLNSParser.xml_declaration))
        qnames, namespaces = ET._namespaces(self._root, self._encod, None)
        namespaces.update(Dictionary(ns).reverse())
        serialize = ET._serialize[self._method]
        serialize(file_dst.write, self._root, self._encod, qnames, namespaces)
        file_dst.close()


class XMLNSParser(object):
    common_xmlns = {
        'xmlns:rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'xmlns:owl': 'http://www.w3.org/2002/07/owl#',
        'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema#',
        'xmlns:rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
    }
    xml_declaration = '<?xml version="1.0"?>'
    
    def __init__(self, source):
        self._ns = self._parse(source)
    
    def get_xmlns(self):
        ns = XMLNSParser.common_xmlns.copy()
        ns.update(self._ns)
        return ns
    
    def get_xmlns_noprefix(self):
        ns = {}
        for k in self.get_xmlns():
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
                        string = '{0}{1}'.format(string, char)
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
        pattern = re.compile('(\S+)\s*=\s*"(\S*)"')
        matches = pattern.findall(string)
        for groups in matches:
            name = groups[0]
            value = groups[1]
            ns[name] = value
        return ns
