# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree

from utils import ElementTreeWriter, PathInfo, XMLNSParser


vocab = {
    'about': u'about',
    'clss' : u'Class',
    'desc' : u'Description',
    'dttp' : u'DatatypeProperty',
    'id'   : u'ID',
    'objp' : u'ObjectProperty',
    'onto' : u'Ontology',
    'rdf'  : u'RDF',
    'rsrc' : u'resource',
    'subc' : u'subClassOf',
}


class Ontology:
    def create(self, dst, ns={}):
        self._save_empty_ontology(dst, ns)
        self.load(dst)
    
    def get_allclasses(self):
        classes = []
        for e in self._root:
            oe = _OntoElem(e, self)
            if oe._is_class():
                classes.append(self._get_class(e))
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
        self.name = self._get_ontology_name(src)
        self._tree = ET.parse(src)
        self._root = self._tree.getroot()
        xmlns_parser = XMLNSParser(src)
        self.ns = xmlns_parser.get_xmlns()
        self.ns_nopre = xmlns_parser.get_xmlns_noprefix()
        for k in self.ns_nopre.keys():
            ET.register_namespace(k, self.ns_nopre[k])
    
    def save(self, dst=None, ns={}):
        dest = self.src
        if dst:
            dest = dst
        namespaces = self.ns_nopre.copy()
        namespaces.update(ns)
        ElementTreeWriter(self._root, dest).write(namespaces)
    
    def _get_class(self, elem):
        oe = _OntoElem(elem, self)
        c = Class(oe.name, self)
        c._elem = elem
        return c
    
    def _get_ontology_name(self, src):
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


class _OntoElem:
    def __init__(self, elem, onto):
        self._elem = elem
        self.onto = onto
        self.name = self._get_name()
    
    def __repr__(self):
        return '<_OntoElem: %s>' % self._elem
    
    def _get_name(self):
        kid = self._get_formated_string('rdf', 'id')
        kab = self._get_formated_string('rdf', 'about')
        if kid in self._elem.keys():
            name = self._elem.get(kid)
        elif kab in self._elem.keys():
            name = self._elem.get(kab)[1:]
        else:
            name = None
        return name
    
    def _get_formated_string(self, prefix, term):
        return '{%s}%s' % (self.onto.ns_nopre[prefix], vocab[term])
    
    def _is_class(self):
        return self._elem.tag == self._get_formated_string('owl', 'clss')
    
    def _is_datatypeproperty(self):
        return self._elem.tag == self._get_formated_string('owl', 'dttp')
    
    def _is_description(self):
        return self._elem.tag == self._get_formated_string('rdf', 'desc')
    
    def _is_instance(self):
        pass
    
    def _is_objectproperty(self):
        return self._elem.tag == self._get_formated_string('owl', 'objp')
    
    def _is_property(self):
        return self._is_datatypeproperty(self) or self._is_objectproperty()
    
    def _is_property_instance(self):
        pass
    
    def _is_subclass_of(self):
        return self._elem.tag == self._get_formated_string('rdfs', 'subc')


class Class(_OntoElem):
    def __init__(self, name, onto):
        self.name = name
        self.onto = onto
        self._elem = self._create_element()
    
    def __repr__(self):
        return '<owl:%s %s>'% (vocab['clss'], self.name)
    
    def _create_element(self):
        tag = self._get_formated_string('owl', 'clss')
        key = self._get_formated_string('rdf', 'id')
        value = self.name
        attrib = {key: value}
        return Element(tag, attrib)
    
    def get_subclasses(self, indirect=False):
        classes = []
        for c in self.onto.get_allclasses():
            if c.name != self.name and \
               c.is_subclass_of(self, indirect) and \
               not c in classes:
                classes.append(c)
        return classes
    
    def get_superclasses(self, indirect=False):
        classes = []
        for c in self.onto.get_allclasses():
            if c.name != self.name and \
               c.is_superclass_of(self, indirect) and \
               not c in classes:
                classes.append(c)
        return classes
    
    def is_mainclass(self):
        return not self.get_superclasses()
    
    def is_subclass_of(self, clss, indirect=False):
        if isinstance(clss, Class):
            cls = clss
            clss_name = clss.name
        elif isinstance(clss, str):
            cls = self.onto.get_class(clss)
            clss_name = clss
        is_subclass = False
        for e1 in self._elem:
            oe1 = _OntoElem(e1, self.onto)
            if oe1._is_subclass_of():
                rsrc = self._get_formated_string('rdf', 'rsrc')
                # <rdfs:subClassOf rdf:resource="#class_name"/>
                rsrc_name = e1.attrib.get(rsrc)
                if rsrc_name:
                    i = rsrc_name.index('#')
                    if rsrc_name[i+1:] == clss_name:
                        is_subclass = True
                        break
                # <rdfs:subClassOf>
                #   <owl:Class rdf:about/ID="#/class_name"/>
                # </rdfs:subClassOf>
                for e2 in e1:
                    oe2 = _OntoElem(e2, self.onto)
                    if (oe2._is_class() or oe2._is_description()) and \
                        oe2.name == clss_name:
                        is_subclass = True
                        break
        if indirect:
            for c in cls.get_subclasses():
                if self.is_subclass_of(c, True):
                    is_subclass = True
                    break
        return is_subclass
    
    def is_superclass_of(self, clss, indirect=False):
        if isinstance(clss, Class):
            c = clss
        elif isinstance(clss, str):
            c = self.onto.get_class(clss)
        return c.is_subclass_of(self, indirect)
