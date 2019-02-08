import oci
import logging


class OCIConfig:

    def __init__(self, config_path=None, **kwargs):
        """
        Init OCIConfig dynamically creating attributes based on the configuration file or command line parameters
        :param config_path: configuration file path
        :param kwargs: command line parameters
        """

        self._compartments_tree = None
        self._workon_region = None
        self._vcn_tree = {}

        profile = kwargs['profile'] if 'profile' in kwargs else 'DEFAULT'

        #self._config = oci.config.from_file(file_location=config_path, profile_name=profile)
        self._config = oci.config.from_file(config_path)
        self._defined_tags = {}
        self._free_tags ={}

        def _set_config_attr(k, v):
            if v:
                # if preserve_tags are provided, parse it
                if k == 'preserve_tags':
                    for tag in v.split(','):
                        try:
                            tag_kv = tag.split('=')
                            tag_value = tag_kv[1] if len(tag_kv) > 1 else ''

                            if tag_kv[0].find('.') > 0:
                                self._defined_tags[tag_kv[0].split('.')[0]] = {
                                                            tag_kv[0].split('.')[1]: tag_value}
                            else:
                                self._free_tags[tag_kv[0]] = tag_value
                        except:
                            logging.error('unable to parse tag {}'.format(tag))

                setattr(self, '_config_{}'.format(k), v.split(',') if isinstance(v, str) and ',' in v else v)

        for key, value in self._config.items():
            _set_config_attr(key, value)

        # set the value from command line
        # note that it overwrites config file value
        for key, value in kwargs.items():
            _set_config_attr(key, value)


    @property
    def tenancy(self):
        return self._config_tenancy

    @property    
    def compartments_scope(self):
        """
        compartment list to work with
        """
        return self._config_compartment if hasattr(self, '_config_compartment') and self._config_compartment else self._config_tenancy
    
    @property
    def compartments_tree(self):
        return self._compartments_tree
    
    @compartments_tree.setter
    def compartments_tree(self,c_tree):
        self._compartments_tree = c_tree

    @property
    def config(self):
        return self._config

    @property
    def workon_region(self):
        if 'region' not in self._config:
            self._config['region'] = None
        return self._config['region']

    @workon_region.setter
    def workon_region(self, region):
        """
        region currently in use
        """
        self._config['region'] = region

    @property
    def region_filter(self):
        if hasattr(self, '_config_region_filter'):
            return self._config_region_filter if isinstance(self._config_region_filter,list) else [self._config_region_filter]
        return None

    @property
    def compartment_filter(self):
        if hasattr(self, '_config_compartment_filter'):
            return self._config_compartment_filter if isinstance(self._config_compartment_filter,list) else [self._config_compartment_filter]
        return None

    @property
    def vcn_filter(self):
        if hasattr(self, '_config_vcn_filter'):
            return self._config_vcn_filter if isinstance(self._config_vcn_filter, list) else [self._config_vcn_filter]
        return None

    @property
    def simulate_deletion(self):
        try:
            if hasattr(self, '_config_simulate_deletion'):
                return self._config_simulate_deletion and self._config_simulate_deletion.lower() == 'true'
        except:
            pass
        return False

    @property
    def operation(self):
        """
        set list as default operation

        :return: operation
        """
        return self._config_operation if hasattr(self, '_config_operation') and self._config_operation else 'list'

    @property
    def preserve_top_level_compartment(self):
        """
        specify if the top level compartment need to be preserved
        :return: configuratino value of preserve_top_level_compartment
        """
        if hasattr(self, '_config_preserve_top_level_compartment'):
            return self._config_preserve_top_level_compartment and self._config_preserve_top_level_compartment.lower() == 'true'
        else:
            return False

    @property
    def preserve_compartments(self):
        """

        :return:
        """
        if hasattr(self, '_config_preserve_compartments'):
            return self._config_preserve_compartments if \
                isinstance(self._config_preserve_compartments, list) \
                else self._config_preserve_compartments
        return None

    @property
    def preserve_compartment_structure(self):
        """
        specify if the compartments structure need to be preserved
        :return: configuration value of preserve_compartment_structure
        """
        if hasattr(self, '_config_preserve_compartment_structure'):
            return self._config_preserve_compartment_structure and self._config_preserve_compartment_structure.lower() == 'true'
        else:
            return False

    @property
    def preserve_tags(self):
        return {'free-tags': self._free_tags, 'defined-tags': self._defined_tags}

    @property
    def skip_scan_preserved_resources(self):
        """
        specify if preserved resources must be scanned
        :return: Default value: True
        """
        if hasattr(self, '_config_skip_scan_preserved_resources'):
            return self._config_skip_scan_preserved_resources and self._config_skip_scan_preserved_resources.lower() == 'true'
        else:
            return True
