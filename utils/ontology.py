# -*- coding: utf-8 -*-


_vocab = {
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


class _OntoElem(object):
    def __init__(self, elem, onto):
        self._elem = elem
        self.onto = onto
        self.name = self._get_name()
    
    def __repr__(self):
        return '<_OntoElem: {0}>'.format(self._elem)
    
    def _get_name(self):
        kid = self._format_prop('rdf', 'id')
        kab = self._format_prop('rdf', 'about')
        name = self._elem.get(kab)
        if name:
            name = name[1:]
        name = self._elem.get(kid, name)
        return name
    
    def _format_name(self, name):
        return '{%s}%s' % (self.onto.ns_nopre[''], name)
    
    def _format_prop(self, prefix, term):
        return '{%s}%s' % (self.onto.ns_nopre[prefix], _vocab[term])
    
    def _is_class(self):
        return self._elem.tag == self._format_prop('owl', 'clss')
    
    def _is_class_instance(self):
        pass
    
    def _is_datatypeproperty(self):
        return self._elem.tag == self._format_prop('owl', 'dttp')
    
    def _is_description(self):
        return self._elem.tag == self._format_prop('rdf', 'desc')
    
    def _is_objectproperty(self):
        return self._elem.tag == self._format_prop('owl', 'objp')
    
    def _is_property(self):
        return self._is_datatypeproperty(self) or self._is_objectproperty()
    
    def _is_property_instance(self):
        pass
    
    def _is_subclass_of(self):
        return self._elem.tag == self._format_prop('rdfs', 'subc')
