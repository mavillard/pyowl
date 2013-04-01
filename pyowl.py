# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree

from utils import ElementTreeWriter, PathInfo, XMLNSParser


types = {
    'clss': u'Class',
    'dttp': u'DatatypeProperty',
    'objp': u'ObjectProperty'
}


class Ontology:
    def create(self, destination, ns={}):
        self._save_empty_ontology(destination, ns)
        self.load(destination)
    
    def get_allclasses(self):
        classes = []
        for e in self._root:
            oe = OntElem(e, self)
            if oe.is_class():
                classes.append(oe.name)
        return classes
    
    def load(self, source):
        self.source = source
        self.name = self._get_ontology_name(source)
        self._tree = ET.parse(source)
        self._root = self._tree.getroot()
        xmlns_parser = XMLNSParser(source)
        self.ns = xmlns_parser.get_xmlns()
        self.ns_nopre = xmlns_parser.get_xmlns_noprefix()
        for k in self.ns_nopre.keys():
            ET.register_namespace(k, self.ns_nopre[k])
    
    def save(self, destination=None, ns={}):
        dst = self.source
        if destination:
            dst = destination
        namespaces = self.ns_nopre
        if ns:
            namespaces = ns
        ElementTreeWriter(self._root, dst).write(namespaces)
    
    def _get_ontology_name(self, source):
        return PathInfo(source).get_file_name_noext()
    
    def _save_empty_ontology(self, destination, ns):
        s = XMLNSParser.xml_declaration
        s = '%s\n<rdf:RDF' % s
        for k in ns.keys():
            s = '%s\n    %s="%s"' % (s, k, ns[k])
        s = '%s>\n\n  <owl:Ontology rdf:about="">' % s
        s = '%s\n  </owl:Ontology>' % s
        s = '%s\n\n</rdf:RDF>' % s
        file_dst = open(destination, "w")
        file_dst.write(s)
        file_dst.close()

class OntElem:
    def __init__(self, elem, ont):
        self.elem = elem
        self.ont = ont
        self.name = self._get_name()
        self.type = self._get_type()
    
    def __repr__(self):
        return self.name
    
    def _get_name(self):
        kid = '{%s}ID' % self.ont.ns['rdf']
        kab = '{%s}about' % self.ont.ns['rdf']
        if kid in self.elem.keys():
            name = self.elem.get(kid)
        elif kab in self.elem.keys():
            name = self.elem.get(kab)[1:]
        else:
            name = ''
        return name
    
    def _get_type(self):
        if self.is_class():
            typ = types['clss']
        elif self.is_datatypeproperty():
            typ = types['dttp']
        elif self.is_objectproperty():
            typ = types['objp']
        else:
            typ = 'unknown'
        return typ
    
    def is_class(self):
        return self.elem.tag == '{%s}%s' % (self.ont.ns['owl'], types['clss'])
    
    def is_datatypeproperty(self):
        return self.elem.tag == '{%s}%s' % (self.ont.ns['owl'], types['dttp'])
    
    def is_objectproperty(self):
        return self.elem.tag == '{%s}%s' % (self.ont.ns['owl'], types['objp'])
    
    def is_property(self):
        return self.is_datatypeproperty(self) or self.is_objectproperty()
    

class Class:
    def __init__(self, name, ont):
        self.name = name
        self.ont = ont
        self.type = types['clss']
