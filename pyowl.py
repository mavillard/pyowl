# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree

from classowl import Class
from utils.ontology import _vocab as vocab, _OntoElem as OE
from utils.path import PathInfo
from utils.xmlparser import ElementTreeWriter, XMLNSParser


class Ontology:
    def create(self, dst, ns={}):
        self._save_empty_ontology(dst, ns)
        self.load(dst)
    
    def get_allclasses(self):
        classes = []
        for e in self._root:
            oe = OE(e, self)
            if oe._is_class():
                classes.append(self._get_class(oe))
        return classes
    
    def get_mainclasses(self):
        classes = []
        for c in self.get_allclasses():
            if c.is_mainclass():
                classes.append(c)
        return classes
    
    def get_class(self, clss_name):
        clss = None
        for c in self.get_allclasses():
            if c.name == clss_name:
                clss = c
                break
        return clss
    
    def load(self, src):
        self.src = src
        self.name = self._get_name(src)
        self._tree = ET.parse(src)
        self._root = self._tree.getroot()
        xmlns_parser = XMLNSParser(src)
        self.ns = xmlns_parser.get_xmlns()
        self.ns_nopre = xmlns_parser.get_xmlns_noprefix()
        for k in self.ns_nopre.keys():
            ET.register_namespace(k, self.ns_nopre[k])
    
    def save(self, dst=None, ns={}):
        if dst:
            dest = dst
        else:
            dest = self.src
        namespaces = self.ns_nopre.copy()
        namespaces.update(ns)
        ElementTreeWriter(self._root, dest).write(namespaces)
    
    def _get_class(self, oe):
        return Class(oe.name, oe.onto, oe._elem)
    
    def _get_name(self, src):
        return PathInfo(src).get_filename_noext()
    
    def _save_empty_ontology(self, dst, ns):
        namespaces = XMLNSParser.common_xmlns.copy()
        namespaces.update(ns)
        s = XMLNSParser.xml_declaration
        s = '%s\n<rdf:%s' % (s, vocab['rdf'])
        for k in namespaces.keys():
            s = '%s\n    %s="%s"' % (s, k, namespaces[k])
        s = '%s>\n\n  <owl:%s rdf:%s="">' % (s, vocab['onto'], vocab['about'])
        s = '%s\n  </owl:%s>' % (s, vocab['onto'])
        s = '%s\n\n</rdf:%s>' % (s, vocab['rdf'])
        file_dst = open(dst, "w")
        file_dst.write(s)
        file_dst.close()
