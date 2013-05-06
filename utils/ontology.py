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


class _OntoElem:
    def __init__(self, elem, onto):
        self._elem = elem
        self.onto = onto
        self.name = self._get_name()
    
    def __repr__(self):
        return '<_OntoElem: %s>' % self._elem
    
    def _get_name(self):
        kid = self._format_string('rdf', 'id')
        kab = self._format_string('rdf', 'about')
        if kid in self._elem.keys():
            name = self._elem.get(kid)
        elif kab in self._elem.keys():
            name = self._elem.get(kab)[1:]
        else:
            name = None
        return name
    
    def _format_string(self, prefix, term):
        return '{%s}%s' % (self.onto.ns_nopre[prefix], _vocab[term])
    
    def _is_class(self):
        return self._elem.tag == self._format_string('owl', 'clss')
    
    def _is_datatypeproperty(self):
        return self._elem.tag == self._format_string('owl', 'dttp')
    
    def _is_description(self):
        return self._elem.tag == self._format_string('rdf', 'desc')
    
    def _is_instance(self):
        pass
    
    def _is_objectproperty(self):
        return self._elem.tag == self._format_string('owl', 'objp')
    
    def _is_property(self):
        return self._is_datatypeproperty(self) or self._is_objectproperty()
    
    def _is_property_instance(self):
        pass
    
    def _is_subclass_of(self):
        return self._elem.tag == self._format_string('rdfs', 'subc')
