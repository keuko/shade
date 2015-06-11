# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

import bunch

import shade
from shade import exc
from shade.tests.unit import base


class TestDomains(base.TestCase):

    def setUp(self):
        super(TestDomains, self).setUp()
        self.cloud = shade.openstack_cloud()

    @mock.patch.object(shade.OpenStackCloud, 'get_identity_domain')
    @mock.patch.object(shade.OpenStackCloud, '_get_project')
    def test_identity_params_v3(self, mock_get_project, mock_get_domain):
        mock_get_project.return_value = bunch.Bunch(id=1234)
        mock_get_domain.return_value = bunch.Bunch(id=5678)

        self.cloud.api_versions = dict(identity='3')

        ret = self.cloud._get_identity_params(domain='foo', project='bar')
        self.assertIn('default_project', ret)
        self.assertEqual(ret['default_project'], 1234)
        self.assertIn('domain', ret)
        self.assertEqual(ret['domain'], 5678)

    @mock.patch.object(shade.OpenStackCloud, 'get_identity_domain')
    @mock.patch.object(shade.OpenStackCloud, '_get_project')
    def test_identity_params_v3_no_domain(
            self, mock_get_project, mock_get_domain):
        mock_get_project.return_value = bunch.Bunch(id=1234)
        mock_get_domain.return_value = bunch.Bunch(id=5678)

        self.cloud.api_versions = dict(identity='3')

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._get_identity_params,
            domain=None, project='bar')

    @mock.patch.object(shade.OpenStackCloud, 'get_identity_domain')
    @mock.patch.object(shade.OpenStackCloud, '_get_project')
    def test_identity_params_v2(self, mock_get_project, mock_get_domain):
        mock_get_project.return_value = bunch.Bunch(id=1234)
        mock_get_domain.return_value = bunch.Bunch(id=5678)

        self.cloud.api_versions = dict(identity='2')

        ret = self.cloud._get_identity_params(domain='foo', project='bar')
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], 1234)
        self.assertNotIn('domain', ret)

    @mock.patch.object(shade.OpenStackCloud, 'get_identity_domain')
    @mock.patch.object(shade.OpenStackCloud, '_get_project')
    def test_identity_params_v2_no_domain(
            self, mock_get_project, mock_get_domain):
        mock_get_project.return_value = bunch.Bunch(id=1234)
        mock_get_domain.return_value = bunch.Bunch(id=5678)

        self.cloud.api_versions = dict(identity='2')

        ret = self.cloud._get_identity_params(domain=None, project='bar')
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], 1234)
        self.assertNotIn('domain', ret)
