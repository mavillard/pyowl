# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree

from utils.ontology import _vocab as vocab, _OntoElem as OE


class Class(OE):
    def __init__(self, name, onto, elem=None):
        self.name = name
        self.onto = onto
        if elem is not None:
            self._elem = elem
        else:
            self._elem = self._create_element()
    
    def __repr__(self):
        return '<owl:%s %s>'% (vocab['clss'], self.name)
    
    def _create_element(self):
        tag = self._format_string('owl', 'clss')
        key = self._format_string('rdf', 'id')
        value = self.name
        attrib = {key: value}
        return Element(tag, attrib)
    
    def get_instances(self, indirect=False):
        pass
    
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
    
    def is_instance_of(self, instance, indirect=False):
        pass
    
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
            oe1 = OE(e1, self.onto)
            if oe1._is_subclass_of():
                rsrc = self._format_string('rdf', 'rsrc')
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
                    oe2 = OE(e2, self.onto)
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
