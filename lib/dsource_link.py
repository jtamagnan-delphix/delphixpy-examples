"""
Create an object to link MS SQL or ASE dSources
"""

from delphixpy.v1_10_2.web import sourceconfig
from delphixpy.v1_10_2.web import group
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import vo

from lib import dlpx_exceptions
from lib import get_references

VERSION = "v.0.3.000"


class DsourceLink:
    """
    Base class for linking dSources
    """
    def __init__(self, dlpx_obj, dsource_name, db_passwd, db_user, dx_group,
                 db_type):
        """
        Attributes required for linking MS SQL or ASE dSources
        :param dlpx_obj: A Delphix DDP session object
        :type dlpx_obj: lib.get_session.GetSession
        :param dsource_name: Name of the dsource
        :type dsource_name: str
        :param dx_group: Group name of where the dSource will reside
        :type dx_group: str
        :param db_passwd: Password of the db_user
        :type db_passwd: str
        :param db_user: Username of the dSource
        :type db_user: str
        :param db_type: dSource type. mssql, sybase or oracle
        :type db_type: str
        """
        self.dlpx_obj = dlpx_obj
        self.group = dx_group
        self.db_passwd = db_passwd
        self.db_user = db_user
        self.dsource_name = dsource_name
        self.db_type = db_type
        self.engine_name = self.dlpx_obj.dlpx_ddps['engine_name']
        self.link_params = vo.LinkParameters()
        self.srccfg_obj = None

    def dsource_prepare_link(self):
        """
        Prepare the dsource object for linking
        """
        self.link_params.name = self.dsource_name
        if self.db_type.lower() == 'oracle':
            self.link_params.link_data = vo.OracleLinkData()
        elif self.db_type.lower() == 'sybase':
            self.link_params.link_data = vo.ASELinkData()
        elif self.db_type.lower() == 'mssql':
            self.link_params.link_data = vo.MSSqlLinkData()
        self.link_params.group = get_references.find_obj_by_name(
            self.dlpx_obj.server_session, group, self.group).reference
        self.link_params.link_data.db_credentials = vo.PasswordCredential()
        self.link_params.link_data.db_credentials.password = self.db_passwd
        self.link_params.link_data.db_user = self.db_user
        self.link_params.link_data.sourcing_policy = vo.SourcingPolicy()
        # Enforce logsync. Set this to False if logsync is not needed
        self.link_params.link_data.sourcing_policy.logsync_enabled = True
        self.link_params.link_data.config = self.get_or_create_sourceconfig()
        return self.link_params

    def get_or_create_sourceconfig(self, sourceconfig_obj=None):
        """
        Get current sourceconfig or create it
        :param sourceconfig_obj:
        :return: link_params
        """
        try:
            return get_references.find_obj_by_name(
                self.dlpx_obj.server_session, sourceconfig,
                self.dsource_name).reference
        except dlpx_exceptions.DlpxObjectNotFound:
            self.link_params.link_data.config = sourceconfig.create(
                self.dlpx_obj.server_session, sourceconfig_obj).reference

#    def build_source_config(self):
#        """
#        Build the source config object
#        :return:
#        """
#        env_obj = get_references.find_obj_by_name(
#            self.dlpx_obj.server_session, environment, env_name)
#        repo_ref = get_references.find_db_repo(
#            self.dlpx_obj.server_session, 'OracleInstall', env_obj.reference,
#            db_install_path)
#        sourcecfg_params = vo.OracleSIConfig()
#        connect_str = f'jdbc:oracle:thin:@{ip_addr}:{port_num}:' \
#                      f'{self.dsource_name}'
#        sourcecfg_params.database_name = self.dsource_name
#        sourcecfg_params.unique_name = self.dsource_name
#        sourcecfg_params.repository = repo_ref
#        sourcecfg_params.instance = vo.OracleInstance()
#        sourcecfg_params.instance.instance_name = self.dsource_name
#        sourcecfg_params.instance.instance_number = 1
#        sourcecfg_params.services = vo.OracleService()
#        sourcecfg_params.jdbcConnectionString = connect_str
#        sourceconfig_ref = self.get_or_create_sourceconfig(sourcecfg_params)
#        self.link_ora_dsource(sourceconfig_ref, env_obj.primary_user)

