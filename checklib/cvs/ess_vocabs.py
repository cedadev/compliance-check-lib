"""
ess_vocabs.py
=============

Holds the ESSVocabs class.

This is a base class for working with controlled vocabularies that can be worked with
using the pyessv library (https://github.com/ES-DOC/pyessv).

For example, the CMIP6 project manages its CVs in GitHub and can be accessed by pyessv
using a local file-system cache of the files.

"""

import os
from netCDF4 import Dataset

# Import library to interact with Controlled Vocabularies
import pyessv


def validate_daterange(frequency):
    if frequency == "yr" or frequency == "decadal":
        template = "yyyy"
    elif frequency == "mon" or frequency == "monClim":
        template = "yyyyMM"
    return template


class ESSVocabs(object):
    """
    Class for working with Vocabularies stored in ESSV format.
    Accessible via `pyessv` library.

    """
    authority = None
    scope = None

    
    def __init__(self, authority, scope):
        """
        Instantiates class by setting authority, scope and loading the CVs 
        from local cache.
        """
        self.authority = authority
        self.scope = scope
        self._cache_controlled_vocabularies()


    def _cache_controlled_vocabularies(self):
        """
        Loads controlled vocabularies once and caches them.
        """
        self._cvs = pyessv.load(self.authority, self.scope)
        self._authority_info = pyessv.load(self.authority)
        self._scope_info = pyessv.load(self.authority, self.scope)


    def _get_lookup_id(self, attr, full=False):
        """
        Maps attribute name to lookup value.

        :attr   attribute name: string
        :full   boolean to say whether the attribute should be expressed
                as a full path: default=False 
                If True: <authority>:<scope>:<attribute>
        :return: lookup value: string
        """
        fixed_attr = attr.replace("_", "-")

        if full:
            return "{}:{}:{}".format(self.authority, self.scope, fixed_attr)
        else:
            return fixed_attr

    def get_value(self, term, property="label"):
        """
        Makes the lookup for a given term and matches against the property given.
        Copes with nested dictionary lookups that are expressed by the "." convention in the value of `attr`.

        :param term: term to lookup.
        :param property: property of term to match against (even including sub-dictionary lookups).
        :return: value or None if not found.
        """
        # Delay nested looks up if required
        if "." in property:
            property, key_chain = property.split(".", 2)
            key_chain = key_chain.split(".")
        else:
            key_chain = []

        # Do vocabulary look-up
        value = getattr(term, property, None)
        if not value:
            return None

        # Now do nested lookup
        for key in key_chain:
            value = value[key]

        return value

    def check_global_attribute(self, ds, attr, property="label"):
        """
        Checks that global attribute `attr` is in allowed values (from CV).
       
        :param ds: NetCDF4 Dataset object
        :param attr: string - name of attribtue to check.
        :param property: string property of CV term to check (defaults to 'label')
        :return: Integer (0: not found; 1: found (not recognised); 2: found and recognised.
        """
        if not attr in ds.ncattrs():
            return 0
           
        nc_attr = ds.getncattr(attr) 
        allowed_values = [self.get_value(term, property) for term in self._cvs[self._get_lookup_id(attr)]]

        if nc_attr not in allowed_values:
            return 1
            
        return 2


    def check_file_name(self, filename, keys=None, delimiter="_", extension=".nc"):
        """
        Checks that components in the file name match CV-allowed values.
        
        E.g.:
        <variable_id>   tas
        <table_id>      Amon
        <source_id>     hadgem3-es
        <experiment_id> piCtrl
        <member_id>     r1i1p1f1
        <grid_label>    gn
        [<time_range>]  201601-210012
        .nc
        
        :param filename: string
        :keys  sequence of attribute keys to look-up values from in CVs.
        :delimiter  string used as delimiter in file name: string.
        :extension  the file extension: string.
        :return: boolean
        """
        if not keys or type(keys) not in (type([]), type(())):
            raise Exception("File name checks require an input of attribute keys to check against. "
                            "None given.")
                            
        items = os.path.splitext(filename)[0].split(delimiter)
        
        # Now check
        template = delimiter.join(['{}' for item in items]) + extension
        collections = tuple([self._get_lookup_id(key, full=True) for key in keys])

        try:
            parser = pyessv.create_template_parser(template, collections)
            parser.parse(filename)
        except pyessv.TemplateParsingError:
            return False

        return True
