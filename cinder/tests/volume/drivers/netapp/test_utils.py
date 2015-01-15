# Copyright (c) - 2014, Rushil Chugh.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cinder import test
import cinder.tests.volume.drivers.netapp.fakes as fake
import cinder.volume.drivers.netapp.utils as na_utils


class NetAppDriverUtilsTestCase(test.TestCase):
    def test_iscsi_connection_properties(self):
        FAKE_LUN_ID = 1

        actual_properties = na_utils.get_iscsi_connection_properties(
            fake.ISCSI_FAKE_ADDRESS, fake.ISCSI_FAKE_PORT,
            fake.ISCSI_FAKE_IQN, FAKE_LUN_ID, fake.ISCSI_FAKE_VOLUME)

        actual_properties_mapped = actual_properties['data']

        self.assertDictEqual(actual_properties_mapped, fake.ISCSI_FAKE_DICT)

    def test_iscsi_connection_lun_id_str(self):
        FAKE_LUN_ID = '1'

        actual_properties = na_utils.get_iscsi_connection_properties(
            fake.ISCSI_FAKE_ADDRESS, fake.ISCSI_FAKE_PORT,
            fake.ISCSI_FAKE_IQN, FAKE_LUN_ID, fake.ISCSI_FAKE_VOLUME)

        actual_properties_mapped = actual_properties['data']

        self.assertIs(type(actual_properties_mapped['target_lun']), int)

    def test_iscsi_connection_lun_id_dict(self):
        FAKE_LUN_ID = {'id': '1'}

        self.assertRaises(TypeError,
                          na_utils.get_iscsi_connection_properties,
                          fake.ISCSI_FAKE_ADDRESS, fake.ISCSI_FAKE_PORT,
                          fake.ISCSI_FAKE_IQN, FAKE_LUN_ID,
                          fake.ISCSI_FAKE_VOLUME)
