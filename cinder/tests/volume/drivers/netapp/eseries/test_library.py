# Copyright (c) 2014 Andrew Kerr
# Copyright (c) 2015 Alex Meade
# Copyright (c) 2015 Rushil Chugh
# Copyright (c) 2015 Yogesh Kshirsagar
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

import copy
import ddt

import mock

from cinder import exception
from cinder import test
from cinder.tests.volume.drivers.netapp.eseries import fakes as \
    eseries_fake
from cinder.tests.volume.drivers.netapp import fakes as na_fakes
from cinder.volume.drivers.netapp.eseries import library
from cinder.volume.drivers.netapp import utils as na_utils
from cinder.zonemanager import utils as fczm_utils


def get_fake_volume():
    return {
        'id': '114774fb-e15a-4fae-8ee2-c9723e3645ef', 'size': 1,
        'volume_name': 'lun1', 'host': 'hostname@backend#DDP',
        'os_type': 'linux', 'provider_location': 'lun1',
        'name_id': '114774fb-e15a-4fae-8ee2-c9723e3645ef',
        'provider_auth': 'provider a b', 'project_id': 'project',
        'display_name': None, 'display_description': 'lun1',
        'volume_type_id': None, 'migration_status': None, 'attach_status':
        "detached"
    }


@ddt.ddt
class NetAppEseriesLibraryTestCase(test.TestCase):
    def setUp(self):
        super(NetAppEseriesLibraryTestCase, self).setUp()

        kwargs = {'configuration': self.get_config_eseries()}

        self.library = library.NetAppESeriesLibrary('FAKE', **kwargs)
        self.library._client = mock.Mock()
        self.library.check_for_setup_error()

    def get_config_eseries(self):
        config = na_fakes.create_configuration_eseries()
        config.netapp_storage_protocol = 'iscsi'
        config.netapp_login = 'rw'
        config.netapp_password = 'rw'
        config.netapp_server_hostname = '127.0.0.1'
        config.netapp_transport_type = 'http'
        config.netapp_server_port = '8080'
        config.netapp_storage_pools = 'DDP'
        config.netapp_storage_family = 'eseries'
        config.netapp_sa_password = 'saPass'
        config.netapp_controller_ips = '10.11.12.13,10.11.12.14'
        config.netapp_webservice_path = '/devmgr/v2'
        return config

    def test_do_setup(self):
        self.mock_object(self.library,
                         '_check_mode_get_or_register_storage_system')
        mock_check_flags = self.mock_object(na_utils, 'check_flags')
        self.library.do_setup(mock.Mock())

        self.assertTrue(mock_check_flags.called)

    def test_update_ssc_info(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'driveMediaType': 'ssd'}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]

        self.library._get_storage_pools = mock.Mock(return_value=pools)
        self.library._client.list_storage_pools = mock.Mock(return_value=[])
        self.library._client.list_drives = mock.Mock(return_value=drives)

        self.library._update_ssc_info()

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'SSD',
                          'netapp_disk_encryption': 'true'}},
                         self.library._ssc_stats)

    def test_update_ssc_disk_types_ssd(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'driveMediaType': 'ssd'}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'SSD'}},
                         ssc_stats)

    def test_update_ssc_disk_types_scsi(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': 'scsi'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'SCSI'}},
                         ssc_stats)

    def test_update_ssc_disk_types_fcal(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': 'fibre'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'FCAL'}},
                         ssc_stats)

    def test_update_ssc_disk_types_sata(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': 'sata'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'SATA'}},
                         ssc_stats)

    def test_update_ssc_disk_types_sas(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': 'sas'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'SAS'}},
                         ssc_stats)

    def test_update_ssc_disk_types_unknown(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': 'unknown'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'unknown'}},
                         ssc_stats)

    def test_update_ssc_disk_types_undefined(self):
        drives = [{'currentVolumeGroupRef': 'test_vg1',
                   'interfaceType': {'driveType': '__UNDEFINED'}}]
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]
        self.library._client.list_drives = mock.Mock(return_value=drives)

        ssc_stats = self.library._update_ssc_disk_types(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_type': 'unknown'}},
                         ssc_stats)

    def test_update_ssc_disk_encryption_SecType_enabled(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'enabled'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_encryption': 'true'}},
                         ssc_stats)

    def test_update_ssc_disk_encryption_SecType_unknown(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'unknown'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_encryption': 'false'}},
                         ssc_stats)

    def test_update_ssc_disk_encryption_SecType_none(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'none'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_encryption': 'false'}},
                         ssc_stats)

    def test_update_ssc_disk_encryption_SecType_capable(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'capable'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_encryption': 'false'}},
                         ssc_stats)

    def test_update_ssc_disk_encryption_SecType_garbage(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'garbage'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertRaises(TypeError, 'test_vg1',
                          {'netapp_disk_encryption': 'false'}, ssc_stats)

    def test_update_ssc_disk_encryption_multiple(self):
        pools = [{'volumeGroupRef': 'test_vg1', 'securityType': 'none'},
                 {'volumeGroupRef': 'test_vg2', 'securityType': 'enabled'}]

        ssc_stats = self.library._update_ssc_disk_encryption(pools)

        self.assertEqual({'test_vg1': {'netapp_disk_encryption': 'false'},
                          'test_vg2': {'netapp_disk_encryption': 'true'}},
                         ssc_stats)

    def test_terminate_connection_iscsi_no_hosts(self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}

        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))

        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_iscsi,
                          get_fake_volume(),
                          connector)

    def test_terminate_connection_iscsi_volume_not_mapped(self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_iscsi,
                          get_fake_volume(),
                          connector)

    def test_terminate_connection_iscsi_volume_mapped(self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        fake_eseries_volume = copy.deepcopy(eseries_fake.VOLUME)
        fake_eseries_volume['listOfMappings'] = [
            eseries_fake.VOLUME_MAPPING
        ]
        self.mock_object(self.library._client, 'delete_volume_mapping')
        self.mock_object(self.library._client, 'get_volume_mappings',
                         mock.Mock(return_value=[eseries_fake.VOLUME_MAPPING]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[fake_eseries_volume]))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST]))

        self.library.terminate_connection_iscsi(get_fake_volume(), connector)

        self.assertTrue(self.library._client.delete_volume_mapping.called)

    def test_terminate_connection_iscsi_not_mapped_initiator_does_not_exist(
            self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST_2]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_hardware_inventory',
                         mock.Mock(
                             return_value=eseries_fake.HARDWARE_INVENTORY))

        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_iscsi,
                          get_fake_volume(),
                          connector)

    def test_initialize_connection_iscsi_volume_not_mapped(self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(return_value=eseries_fake.VOLUME_MAPPING))
        self.mock_object(self.library._client, 'list_hardware_inventory',
                         mock.Mock(
                             return_value=eseries_fake.HARDWARE_INVENTORY))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST]))
        self.mock_object(self.library._client, 'list_host_types',
                         mock.Mock(return_value=eseries_fake.HOST_TYPES))

        self.library.initialize_connection_iscsi(get_fake_volume(), connector)

        self.assertTrue(self.library._map_volume_to_host.called)

    def test_initialize_connection_iscsi_volume_not_mapped_host_does_not_exist(
            self):
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'get_volume_mappings',
                         mock.Mock(return_value=[]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(return_value=eseries_fake.VOLUME_MAPPING))
        self.mock_object(self.library._client, 'list_hardware_inventory',
                         mock.Mock(
                             return_value=eseries_fake.HARDWARE_INVENTORY))
        self.mock_object(self.library._client, 'list_host_types',
                         mock.Mock(return_value=eseries_fake.HOST_TYPES))

        self.library.initialize_connection_iscsi(get_fake_volume(), connector)

        self.assertTrue(self.library._map_volume_to_host.called)

    def test_initialize_connection_iscsi_volume_already_mapped_to_target_host(
            self):
        """Should be a no-op"""
        connector = {'initiator': eseries_fake.INITIATOR_NAME}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_hardware_inventory',
                         mock.Mock(
                             return_value=eseries_fake.HARDWARE_INVENTORY))
        self.mock_object(self.library._client, 'get_volume_mappings',
                         mock.Mock(return_value=[eseries_fake.VOLUME_MAPPING]))
        self.mock_object(self.library._client, 'create_volume_mapping')
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST]))
        self.mock_object(self.library._client, 'list_host_types',
                         mock.Mock(return_value=eseries_fake.HOST_TYPES))

        self.library.initialize_connection_iscsi(get_fake_volume(), connector)

        self.assertFalse(self.library._client.create_volume_mapping.called)

    @ddt.data(eseries_fake.WWPN,
              fczm_utils.get_formatted_wwn(eseries_fake.WWPN))
    def test_get_host_with_matching_port_wwpn(self, port_id):
        port_ids = [port_id]
        host = copy.deepcopy(eseries_fake.HOST)
        host.update(
            {
                'hostSidePorts': [{'label': 'NewStore', 'type': 'fc',
                                   'address': eseries_fake.WWPN}]
            }
        )
        host_2 = copy.deepcopy(eseries_fake.HOST_2)
        host_2.update(
            {
                'hostSidePorts': [{'label': 'NewStore', 'type': 'fc',
                                   'address': eseries_fake.WWPN_2}]
            }
        )
        host_list = [host, host_2]
        self.mock_object(self.library._client,
                         'list_hosts',
                         mock.Mock(return_value=host_list))

        actual_host = self.library._get_host_with_matching_port(
            port_ids)

        self.assertEqual(host, actual_host)

    def test_get_host_with_matching_port_iqn(self):
        port_ids = [eseries_fake.INITIATOR_NAME]
        host = copy.deepcopy(eseries_fake.HOST)
        host.update(
            {
                'hostSidePorts': [{'label': 'NewStore', 'type': 'iscsi',
                                   'address': eseries_fake.INITIATOR_NAME}]
            }
        )
        host_2 = copy.deepcopy(eseries_fake.HOST_2)
        host_2.update(
            {
                'hostSidePorts': [{'label': 'NewStore', 'type': 'iscsi',
                                   'address': eseries_fake.INITIATOR_NAME_2}]
            }
        )
        host_list = [host, host_2]
        self.mock_object(self.library._client,
                         'list_hosts',
                         mock.Mock(return_value=host_list))

        actual_host = self.library._get_host_with_matching_port(
            port_ids)

        self.assertEqual(host, actual_host)

    def test_terminate_connection_fc_no_hosts(self):
        connector = {'wwpns': [eseries_fake.WWPN]}

        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[]))

        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_fc,
                          get_fake_volume(),
                          connector)

    def test_terminate_connection_fc_volume_not_mapped(self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_host = copy.deepcopy(eseries_fake.HOST)
        fake_host['hostSidePorts'] = [{
            'label': 'NewStore',
            'type': 'fc',
            'address': eseries_fake.WWPN
        }]
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[fake_host]))
        self.mock_object(self.library._client, 'get_volume_mappings_for_host',
                         mock.Mock(return_value=[]))

        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_fc,
                          get_fake_volume(),
                          connector)

    def test_terminate_connection_fc_volume_mapped(self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_host = copy.deepcopy(eseries_fake.HOST)
        fake_host['hostSidePorts'] = [{
            'label': 'NewStore',
            'type': 'fc',
            'address': eseries_fake.WWPN
        }]
        fake_eseries_volume = copy.deepcopy(eseries_fake.VOLUME)
        fake_eseries_volume['listOfMappings'] = [
            copy.deepcopy(eseries_fake.VOLUME_MAPPING)
        ]
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[fake_host]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[fake_eseries_volume]))
        self.mock_object(self.library._client, 'get_volume_mappings_for_host',
                         mock.Mock(return_value=[
                             copy.deepcopy(eseries_fake.VOLUME_MAPPING)]))
        self.mock_object(self.library._client, 'delete_volume_mapping')

        self.library.terminate_connection_fc(get_fake_volume(), connector)

        self.assertTrue(self.library._client.delete_volume_mapping.called)

    def test_terminate_connection_fc_volume_mapped_no_cleanup_zone(self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_host = copy.deepcopy(eseries_fake.HOST)
        fake_host['hostSidePorts'] = [{
            'label': 'NewStore',
            'type': 'fc',
            'address': eseries_fake.WWPN
        }]
        expected_target_info = {
            'driver_volume_type': 'fibre_channel',
            'data': {},
        }
        fake_eseries_volume = copy.deepcopy(eseries_fake.VOLUME)
        fake_eseries_volume['listOfMappings'] = [
            copy.deepcopy(eseries_fake.VOLUME_MAPPING)
        ]
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[fake_host]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[fake_eseries_volume]))
        self.mock_object(self.library._client, 'delete_volume_mapping')
        self.mock_object(self.library._client, 'get_volume_mappings_for_host',
                         mock.Mock(return_value=[
                             copy.deepcopy(eseries_fake.VOLUME_MAPPING)]))

        target_info = self.library.terminate_connection_fc(get_fake_volume(),
                                                           connector)
        self.assertDictEqual(expected_target_info, target_info)

        self.assertTrue(self.library._client.delete_volume_mapping.called)

    def test_terminate_connection_fc_volume_mapped_cleanup_zone(self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_host = copy.deepcopy(eseries_fake.HOST)
        fake_host['hostSidePorts'] = [{
            'label': 'NewStore',
            'type': 'fc',
            'address': eseries_fake.WWPN
        }]
        expected_target_info = {
            'driver_volume_type': 'fibre_channel',
            'data': {
                'target_wwn': [eseries_fake.WWPN_2],
                'initiator_target_map': {
                    eseries_fake.WWPN: [eseries_fake.WWPN_2]
                },
            },
        }
        fake_eseries_volume = copy.deepcopy(eseries_fake.VOLUME)
        fake_eseries_volume['listOfMappings'] = [
            copy.deepcopy(eseries_fake.VOLUME_MAPPING)
        ]
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[fake_host]))
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[fake_eseries_volume]))
        self.mock_object(self.library._client, 'delete_volume_mapping')
        self.mock_object(self.library._client, 'get_volume_mappings_for_host',
                         mock.Mock(return_value=[]))
        self.mock_object(self.library._client, 'list_target_wwpns',
                         mock.Mock(return_value=[eseries_fake.WWPN_2]))

        target_info = self.library.terminate_connection_fc(get_fake_volume(),
                                                           connector)
        self.assertDictEqual(expected_target_info, target_info)

        self.assertTrue(self.library._client.delete_volume_mapping.called)

    def test_terminate_connection_fc_not_mapped_host_with_wwpn_does_not_exist(
            self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[eseries_fake.HOST_2]))
        self.assertRaises(exception.NotFound,
                          self.library.terminate_connection_fc,
                          get_fake_volume(),
                          connector)

    def test_initialize_connection_fc_volume_not_mapped(self):
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_host = copy.deepcopy(eseries_fake.HOST)
        fake_host['hostSidePorts'] = [{'label': 'NewStore',
                                       'type': 'fc',
                                       'address': eseries_fake.WWPN}]
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(return_value=eseries_fake.VOLUME_MAPPING))
        self.mock_object(self.library._client, 'list_hosts',
                         mock.Mock(return_value=[fake_host]))
        self.mock_object(self.library._client, 'list_host_types',
                         mock.Mock(return_value=eseries_fake.HOST_TYPES))
        self.mock_object(self.library._client, 'list_target_wwpns',
                         mock.Mock(return_value=[eseries_fake.WWPN_2]))
        expected_target_info = {
            'driver_volume_type': 'fibre_channel',
            'data': {
                'target_discovered': True,
                'target_lun': 0,
                'target_wwn': [eseries_fake.WWPN_2],
                'access_mode': 'rw',
                'initiator_target_map': {
                    eseries_fake.WWPN: [eseries_fake.WWPN_2]
                }
            },
        }

        target_info = self.library.initialize_connection_fc(get_fake_volume(),
                                                            connector)

        self.assertDictEqual(expected_target_info, target_info)

    def test_initialize_connection_fc_volume_already_mapped_to_target_host(
            self):
        """Should be a no-op"""
        connector = {'wwpns': [eseries_fake.WWPN]}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library._client, 'list_target_wwpns',
                         mock.Mock(return_value=[
                             eseries_fake.FC_TARGET_WWPNS]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(return_value=eseries_fake.VOLUME_MAPPING))

        self.library.initialize_connection_fc(get_fake_volume(), connector)

        self.assertTrue(self.library._map_volume_to_host.called)

    def test_initialize_connection_fc_volume_mapped_to_another_host(self):
        """Should raise error saying multiattach not enabled"""
        connector = {'wwpns': [eseries_fake.WWPN]}
        fake_mapping_to_other_host = copy.deepcopy(
            eseries_fake.VOLUME_MAPPING)
        fake_mapping_to_other_host['mapRef'] = eseries_fake.HOST_2[
            'hostRef']
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(
                             side_effect=exception.NetAppDriverException))

        self.assertRaises(exception.NetAppDriverException,
                          self.library.initialize_connection_fc,
                          get_fake_volume(), connector)

        self.assertTrue(self.library._map_volume_to_host.called)

    def test_initialize_connection_fc_no_target_wwpns(self):
        """Should be a no-op"""
        connector = {'wwpns': [eseries_fake.WWPN]}
        self.mock_object(self.library._client, 'list_volumes',
                         mock.Mock(return_value=[eseries_fake.VOLUME]))
        self.mock_object(self.library, '_map_volume_to_host',
                         mock.Mock(return_value=eseries_fake.VOLUME_MAPPING))
        self.mock_object(self.library._client, 'list_target_wwpns',
                         mock.Mock(return_value=[]))

        self.assertRaises(exception.VolumeBackendAPIException,
                          self.library.initialize_connection_fc,
                          get_fake_volume(), connector)
        self.assertTrue(self.library._map_volume_to_host.called)

    def test_build_initiator_target_map_fc_with_lookup_service(
            self):
        connector = {'wwpns': [eseries_fake.WWPN, eseries_fake.WWPN_2]}
        self.library.lookup_service = mock.Mock()
        self.library.lookup_service.get_device_mapping_from_network = (
            mock.Mock(return_value=eseries_fake.FC_FABRIC_MAP))
        self.mock_object(self.library._client, 'list_target_wwpns',
                         mock.Mock(return_value=[
                             eseries_fake.FC_TARGET_WWPNS]))

        (target_wwpns, initiator_target_map, num_paths) = (
            self.library._build_initiator_target_map_fc(connector))

        self.assertSetEqual(set(eseries_fake.FC_TARGET_WWPNS),
                            set(target_wwpns))
        self.assertDictEqual(eseries_fake.FC_I_T_MAP, initiator_target_map)
        self.assertEqual(4, num_paths)
