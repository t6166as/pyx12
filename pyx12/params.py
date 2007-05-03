######################################################################
# Copyright (c) 2001-2005 Kalamazoo Community Mental Health Services,
#   John Holland <jholland@kazoocmh.org> <john@zoner.org>
# All rights reserved.
#
# This software is licensed as described in the file LICENSE.txt, which
# you should have received as part of this distribution.
#
######################################################################

#    $Id$

"""
Holds Run-time Parameters

Order of precedence:
 1. set(param) - Command line parameters
 2. Config files as constructor parameters
 3. self.params - Defaults
"""
import os.path
import sys
#import StringIO
import libxml2
import logging

NodeType = {'element_start': 1, 'element_end': 15, 'attrib': 2, 'text': 3,
    'CData': 4, 'entity_ref': 5, 'entity_decl':6, 'pi': 7, 'comment': 8,
    'doc': 9, 'dtd': 10, 'doc_frag': 11, 'notation': 12}

class ParamsBase(object):
    """
    Base class for parameters
    """
    def __init__(self):
        self.logger = logging.getLogger('pyx12.params')
        self.params = {}
        self.params['map_path'] = os.path.join(sys.prefix, 'share/pyx12/map')
        self.params['pickle_path'] = os.path.join(sys.prefix, 'share/pyx12/map')
        self.params['exclude_external_codes'] = None
        self.params['ignore_syntax'] = False
        self.params['charset'] = 'E'
        self.params['ignore_codes'] = False
        self.params['ignore_ext_codes'] = False
        self.params['skip_html'] = False
        self.params['skip_997'] = False
        self.params['simple_dtd'] = ''
        self.params['idtag_dtd'] = ''
        self.params['idtagqual_dtd'] = ''
        #self.params['idtag_dtd'] = 'http://www.kazoocmh.org/x12idtag.dtd'
        self.params['xmlout'] = 'simple'
        #self.params['xmlout'] = 'idtag'
        self.params['xslt_files'] = []
        
    def get(self, option):
        """
        Get the value of the parameter specified by option
        @param option: Option name
        @type option: string
        """
        if option in self.params.keys():
            return self.params[option]
        else:
            return None

    def set(self, option, value):
        """
        Set the value of the parameter specified by option
        @param option: Option name
        @type option: string
        @param value: Parameter value
        @type value: string
        """
        if value == '':
            self.params[option] = None
        else:
            self.params[option] = value

    
class ParamsUnix(ParamsBase):
    """
    Read options from XML configuration files
    """
    def __init__(self, *config_files):
        ParamsBase.__init__(self)
        #self.params['map_path'] = '/usr/local/share/pyx12/map'
        #self.params['pickle_path'] = '/usr/local/share/pyx12/map'
        
        for filename in config_files:
            self.logger.debug('Read param file: %s' % (filename))
            self._read_config_file(filename)

    def _read_config_file(self, filename):
        """
        Read program configuration from an XML file

        @param filename: XML file
        @type filename: string
        @return: None
        """
        try:
            if os.path.isfile(filename):
                reader = libxml2.newTextReaderFilename(filename)
                ret = reader.Read()
                while ret == 1:
                    tmpNodeType = reader.NodeType()
                    if tmpNodeType == NodeType['element_start']:
                        cur_name = reader.Name()
                        if cur_name == 'param':
                            option = None
                            value = None
                            valtype = None
                            while reader.MoveToNextAttribute():
                                if reader.Name() == 'name':
                                    option = reader.Value()
                    elif tmpNodeType == NodeType['element_end']:
                        if option is not None:
                            self._set_option(option, value, valtype)
                    elif tmpNodeType == NodeType['text']:
                        if cur_name == 'value':
                            value = reader.Value()
                        elif cur_name == 'type':
                            valtype = reader.Value()
                    ret = reader.Read()
        except:
            self.logger.error('Read of configuration file "%s" failed' % \
                (filename))
            raise

    def _set_option(self, option, value, valtype):
        """
        Set the value of the parameter specified by option
        @param option: Option name
        @type option: string
        @param value: Parameter value
        @type value: string
        @param valtype: Parameter type
        @type valtype: string
        """
        if value == '':
            value = None
        if valtype == 'boolean':
            if value in ('False', 'F'):
                self.params[option] = False
            else:
                self.params[option] = True
        else:
            try:
                if self.params[option] != value:
                    self.params[option] = value
                    #self.logger.debug('Params: option "%s": "%s"' % \
                    #    (option, self.params[option]))
            except:
                self.params[option] = value
                #self.logger.debug('Params: option "%s": "%s"' % \
                #   (option, self.params[option]))
        #self.logger.debug('Params: option "%s": "%s"' % \
        #    (option, self.params[option]))


class ParamsWindows(ParamsBase):
    """
    Read options from the Windows registry
    """
    def __init__(self):
        ParamsBase.__init__(self)
#        self.params['map_path'] = '/usr/local/share/pyx12/map'
#        self.params['pickle_path'] = '/usr/local/share/pyx12/map'
        # Read from Registry
        import _winreg
        #option = Key(key=HKEY.CURRENT_USER, sub_key='Software\\pyx12').values


#if sys.platform == 'win32':
#    params = ParamsWindows
#else:
params = ParamsUnix