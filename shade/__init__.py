# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import warnings

import keystoneauth1.exceptions
import os_client_config
import pbr.version
import requestsexceptions

from shade.exc import *  # noqa
from shade.openstackcloud import OpenStackCloud
from shade.operatorcloud import OperatorCloud
from shade import _log

__version__ = pbr.version.VersionInfo('shade').version_string()

if requestsexceptions.SubjectAltNameWarning:
    warnings.filterwarnings(
        'ignore', category=requestsexceptions.SubjectAltNameWarning)


def _get_openstack_config(app_name=None, app_version=None):
    # Protect against older versions of os-client-config that don't expose this
    kwargs = {}
    try:
        init = os_client_config.OpenStackConfig.__init__
        if 'app_name' in init.im_func.func_code.co_varnames:
            kwargs['app_name'] = app_name
            kwargs['app_version'] = app_version
    except AttributeError:
        # If we get an attribute error, it's actually likely some mocking issue
        # but basically nothing about this is important enough to break things
        # for someone.
        pass
    return os_client_config.OpenStackConfig(**kwargs)


def simple_logging(debug=False, http_debug=False):
    if http_debug:
        debug = True
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    if http_debug:
        # Enable HTTP level tracing
        log = _log.setup_logging('keystoneauth')
        log.addHandler(logging.StreamHandler())
        log.setLevel(log_level)
    # Simple case - we only care about request id log during debug
    log = _log.setup_logging('shade.request_ids')
    log.setLevel(log_level)
    log = _log.setup_logging('shade')
    log.addHandler(logging.StreamHandler())
    log.setLevel(log_level)
    # Suppress warning about keystoneauth loggers
    log = _log.setup_logging('keystoneauth.identity.base')
    log = _log.setup_logging('keystoneauth.identity.generic.base')


def openstack_clouds(
        config=None, debug=False, cloud=None, strict=False,
        app_name=None, app_version=None):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        if cloud is None:
            return [
                OpenStackCloud(
                    cloud=f.name, debug=debug,
                    cloud_config=f,
                    strict=strict,
                    **f.config)
                for f in config.get_all_clouds()
            ]
        else:
            return [
                OpenStackCloud(
                    cloud=f.name, debug=debug,
                    cloud_config=f,
                    strict=strict,
                    **f.config)
                for f in config.get_all_clouds()
                if f.name == cloud
            ]
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))


def openstack_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OpenStackCloud(cloud_config=cloud_config, strict=strict)


def operator_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if 'interface' not in kwargs:
        kwargs['interface'] = 'admin'
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OperatorCloud(cloud_config=cloud_config, strict=strict)
