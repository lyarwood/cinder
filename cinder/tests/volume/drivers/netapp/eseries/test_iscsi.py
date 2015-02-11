# Copyright (c) 2015 Alex Meade, Inc.
# All Rights Reserved.
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

"""
Tests for NetApp e-series iscsi volume driver.
"""

import mock
import requests

from cinder import exception
from cinder.openstack.common import log as logging
from cinder import test
from cinder.tests.volume.drivers.netapp.eseries import fakes
from cinder.volume.drivers.netapp import common


LOG = logging.getLogger(__name__)


class NetAppEseriesIscsiDriverMappingTestCase(test.TestCase):
    """Test case for mapping luns in NetApp e-series iscsi driver."""

    host_ref = '8400000060080E500023C73400300381515BFBA3'
    host_ref_2 = '6400000060080E500023C73400300381515BFBA3'
    eseries_host = {
        "isSAControlled": False,
        "confirmLUNMappingCreation": False,
        "label": "stlrx300s7-55",
        "isLargeBlockFormatHost": False,
        "clusterRef": '0000000000000000000000000000000000000000',
        "protectionInformationCapableAccessMethod": False,
        "ports": [],
        "hostRef": host_ref,
        "hostTypeIndex": 6
    }
    eseries_host_2 = {
        "isSAControlled": False,
        "confirmLUNMappingCreation": False,
        "label": "stlrx300s7-55",
        "isLargeBlockFormatHost": False,
        "clusterRef": "0000000000000000000000000000000000000000",
        "protectionInformationCapableAccessMethod": False,
        "ports": [],
        "hostRef": host_ref_2,
        "hostTypeIndex": 6
    }
    eseries_host_in_group = {
        "isSAControlled": False,
        "confirmLUNMappingCreation": False,
        "label": "stlrx300s7-55",
        "isLargeBlockFormatHost": False,
        "clusterRef": "8500000060080E500023C7340036035F515B78FC",
        "protectionInformationCapableAccessMethod": False,
        "ports": [],
        "hostRef": host_ref,
        "hostTypeIndex": 6
    }
    eseries_host_in_group_2 = {
        "isSAControlled": False,
        "confirmLUNMappingCreation": False,
        "label": "stlrx300s7-55",
        "isLargeBlockFormatHost": False,
        "clusterRef": "8500000060080E500023C7340036035F515B78FC",
        "protectionInformationCapableAccessMethod": False,
        "ports": [],
        "hostRef": host_ref_2,
        "hostTypeIndex": 6
    }
    eseries_host_group = {
        'clusterRef': '8500000060080E500023C7340036035F515B78FC',
    }
    eseries_host_1_mapping = {
        'lunMappingRef': '8800000000000000000000000000000000000000',
        'mapRef': host_ref,
        'volumeRef': 'YFDXJ67BLJH25DXCZFZD4NSF54',
        'perms': 15,
        'ssid': 16384,
        'type': 'all',
        'lun': 0
    }
    eseries_host_2_mapping = {
        'lunMappingRef': '8800000000000000000000000000000000000000',
        'mapRef': host_ref_2,
        'volumeRef': 'YFDXJ67BLJH25DXCZFZD4NSF54',
        'perms': 15,
        'ssid': 16384,
        'type': 'all',
        'lun': 1
    }
    eseries_host_group_mapping = {
        'lunMappingRef': '8800000000000000000000000000000000000001',
        'mapRef': '6400000060080E500023C73400300381515BFBA3',
        'volumeRef': 'DFDXJ67BLJH25DXCZFZD4NSF54',
        'perms': 15,
        'ssid': 16384,
        'type': 'cluster',
        'lun': 1
    }
    eseries_volume_1 = {
        'volumeRef': 'YFDXJ67BLJH25DXCZFZD4NSF54',
        'label': 'VOLUME'
    }

    initiator = 'iqn.1998-01.com.vmware:localhost-28a58148'

    def setUp(self):
        super(NetAppEseriesIscsiDriverMappingTestCase, self).setUp()
        self.configuration = fakes.set_config(fakes.create_configuration())
        self.driver = common.NetAppDriver(configuration=self.configuration)
        requests.Session = mock.Mock(wraps=fakes.FakeEseriesHTTPSession)
        self.driver.do_setup(context='context')
        self.driver.check_for_setup_error()

    def test_map_volume_to_host_already_mapped(self):
        """Test mapping a volume to a host it is already mapped to."""
        # Volume is already mapped to host 1
        maps = [self.eseries_host_1_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)

        mapping = self.driver._map_volume_to_host(self.eseries_volume_1,
                                                  self.initiator)
        # Existing mapping should be returned
        self.assertEqual(self.eseries_host_1_mapping, mapping)

    def test_map_volume_to_host_not_previously_mapped(self):
        """Test mapping an unmapped volume to a host."""
        # Volume is not already mapped
        self.driver._client.get_volume_mappings = mock.Mock(return_value=[])

        mapping = self.driver._map_volume_to_host(self.eseries_volume_1,
                                                  self.initiator)
        self.assertEqual(self.eseries_host_1_mapping, mapping)

    def test_map_volume_to_host_already_mapped_to_host_group(self):
        """Test mapping a volume that is already mapped to a host group.
        This should raise an error as it is not supported.
        """
        # Volume is already mapped to host group
        maps = [self.eseries_host_group_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)

        self.assertRaises(exception.NetAppDriverException,
                          self.driver._map_volume_to_host,
                          self.eseries_volume_1,
                          self.initiator)

    def test_map_volume_to_host_already_mapped_to_host_in_group(self):
        """Test mapping a volume that is already mapped to a host that
        is in a host group. This should raise an error as it is not supported.
        """
        # Volume is already mapped to host 2, which is in the host group
        maps = [self.eseries_host_2_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_in_group)

        self.assertRaises(exception.NetAppDriverException,
                          self.driver._map_volume_to_host,
                          self.eseries_volume_1,
                          self.initiator)

    def test_map_volume_to_host_mapped_but_dest_host_in_group(self):
        """Test mapping a volume, that is already mapped to host 1, to a host
        that is in a host group. This should raise an exception.
        """
        # Volume is already mapped to host 1
        maps = [self.eseries_host_1_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_in_group_2)

        self.assertRaises(exception.NetAppDriverException,
                          self.driver._map_volume_to_host,
                          self.eseries_volume_1,
                          self.initiator)

    def test_map_volume_to_host_already_mapped_lun_id_in_use(self):
        """Test mapping a volume, that is already mapped to host 1, to a host
        that is in a host group but has a mapping with a LUN id already in use
        by the new host. The result should be an Exception since ONTAP cannot
        move the mapping due to a LUN id conflict.
        """
        # Volume is already mapped to host 1
        maps = [self.eseries_host_1_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_in_group_2)
        self.driver._client.is_lun_free = mock.Mock(return_value=False)

        self.assertRaises(exception.NetAppDriverException,
                          self.driver._map_volume_to_host,
                          self.eseries_volume_1,
                          self.initiator)

    def test_map_volume_to_host_already_mapped_src_host_not_in_group(self):
        """Test mapping a volume that is already mapped to a host 1 that is not
        in a host group. The result should be a mapping to a host group
        containing both the existing host and new host.
        """
        # Volume is already mapped to host 1
        maps = [self.eseries_host_1_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)
        # Trying to map to host 2
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_2)
        self.driver._client.get_host = mock.Mock(
            return_value=self.eseries_host)
        self.driver._client.is_lun_free = mock.Mock(return_value=True)
        self.driver._client.create_host_group = mock.Mock(
            return_value=self.eseries_host_group)
        self.driver._client.move_volume_mapping_via_symbol = mock.Mock(
            return_value=self.eseries_host_group_mapping)

        mapping = self.driver._map_volume_to_host(self.eseries_volume_1,
                                                  self.initiator)

        self.assertEqual(self.eseries_host_group_mapping, mapping)
        # ensure host group is made
        self.assertTrue(self.driver._client.create_host_group.called)
        # ensure mapping is moved
        self.assertTrue(
            self.driver._client.move_volume_mapping_via_symbol.called)

    def test_map_volume_to_host_already_mapped_src_host_not_in_group_lun_coll(
            self):
        """Test mapping a volume that is already mapped to host 1 that is not
        in a host group but has a mapping with a LUN id already in use by the
        new host. The result should be an Exception since ONTAP cannot move
        the mapping due to a LUN id conflict.
        """
        # Volume is already mapped to host 1
        maps = [self.eseries_host_1_mapping]
        self.driver._client.get_volume_mappings = mock.Mock(return_value=maps)
        # Trying to map to host 2
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_2)
        self.driver._client.get_host = mock.Mock(
            return_value=self.eseries_host)
        self.driver._client.is_lun_free = mock.Mock(return_value=False)

        self.assertRaises(exception.NetAppDriverException,
                          self.driver._map_volume_to_host,
                          self.eseries_volume_1, self.initiator)

    def test_unmap_volume_from_host_not_mapped(self):
        """Test unmapping a volume that is not mapped is a noop."""
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host)
        self.driver._client.get_volume_mappings = mock.Mock(return_value=[])

        self.assertIsNone(self.driver._unmap_volume_from_host(
                          self.eseries_volume_1, self.initiator))
        self.assertTrue(self.driver._client.get_volume_mappings.called)

    def test_unmap_volume_from_host_mapped_to_host_not_in_group(self):
        """Test unmapping a volume that is mapped directly to a host."""
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host)
        # Volume is mapped to host 1
        self.driver._client.get_volume_mappings = mock.Mock(return_value=[
            self.eseries_host_1_mapping])
        self.driver._client.delete_volume_mapping = mock.Mock()

        self.driver._unmap_volume_from_host(self.eseries_volume_1,
                                            self.initiator)

        self.assertTrue(self.driver._client.delete_volume_mapping.called)

    def test_unmap_volume_from_host_mapped_to_two_hosts_in_group(self):
        """Test unmapping a volume that is mapped to a host group containing
        two hosts.
        """
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_in_group)
        # Volume is mapped to host group
        self.driver._client.get_volume_mappings = mock.Mock(return_value=[
            self.eseries_host_group_mapping])
        self.driver._client.set_host_group_for_host = mock.Mock()
        self.driver._client.list_hosts_in_host_group = mock.Mock(
            return_value=[self.eseries_host_in_group_2])
        self.driver._client.move_volume_mapping_via_symbol = mock.Mock()
        self.driver._client.delete_host_group = mock.Mock()

        self.driver._unmap_volume_from_host(self.eseries_volume_1,
                                            self.initiator)

        self.assertEqual(
            2, self.driver._client.set_host_group_for_host.call_count)
        self.assertTrue(
            self.driver._client.move_volume_mapping_via_symbol.called)
        self.assertTrue(self.driver._client.delete_host_group.called)

    def test_unmap_volume_from_host_mapped_to_one_host_in_group(self):
        """Test unmapping a volume that is mapped to a host group containing
        a single host.
        """
        self.driver._get_or_create_host = mock.Mock(
            return_value=self.eseries_host_in_group)
        # Volume is mapped to host group
        self.driver._client.get_volume_mappings = mock.Mock(return_value=[
            self.eseries_host_group_mapping])
        self.driver._client.set_host_group_for_host = mock.Mock()
        self.driver._client.move_volume_mapping_via_symbol = mock.Mock()
        self.driver._client.list_hosts_in_host_group = mock.Mock(
            return_value=[])
        self.driver._client.delete_host_group = mock.Mock()

        self.driver._unmap_volume_from_host(self.eseries_volume_1,
                                            self.initiator)

        self.driver._client.set_host_group_for_host.assert_called_once_with(
            self.host_ref)
        self.assertFalse(
            self.driver._client.move_volume_mapping_via_symbol.called)
        self.assertTrue(self.driver._client.delete_host_group.called)
