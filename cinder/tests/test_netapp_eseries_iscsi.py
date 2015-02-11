# Copyright (c) 2014 NetApp, Inc.
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
import six.moves.urllib.parse as urlparse

from cinder import exception
from cinder.openstack.common import log as logging
from cinder import test
from cinder.tests.volume.drivers.netapp.eseries import fakes
from cinder.volume.drivers.netapp import common


LOG = logging.getLogger(__name__)


class NetAppEseriesIscsiDriverTestCase(test.TestCase):
    """Test case for NetApp e-series iscsi driver."""

    volume = {'id': '114774fb-e15a-4fae-8ee2-c9723e3645ef', 'size': 1,
              'volume_name': 'lun1',
              'os_type': 'linux', 'provider_location': 'lun1',
              'name_id': '114774fb-e15a-4fae-8ee2-c9723e3645ef',
              'provider_auth': 'provider a b', 'project_id': 'project',
              'display_name': None, 'display_description': 'lun1',
              'volume_type_id': None}
    snapshot = {'id': '17928122-553b-4da9-9737-e5c3dcd97f75',
                'volume_id': '114774fb-e15a-4fae-8ee2-c9723e3645ef',
                'size': 2, 'volume_name': 'lun1',
                'volume_size': 2, 'project_id': 'project',
                'display_name': None, 'display_description': 'lun1',
                'volume_type_id': None}
    volume_sec = {'id': 'b6c01641-8955-4917-a5e3-077147478575',
                  'size': 2, 'volume_name': 'lun1',
                  'os_type': 'linux', 'provider_location': 'lun1',
                  'name_id': 'b6c01641-8955-4917-a5e3-077147478575',
                  'provider_auth': None, 'project_id': 'project',
                  'display_name': None, 'display_description': 'lun1',
                  'volume_type_id': None}
    volume_clone = {'id': 'b4b24b27-c716-4647-b66d-8b93ead770a5', 'size': 3,
                    'volume_name': 'lun1',
                    'os_type': 'linux', 'provider_location': 'cl_sm',
                    'name_id': 'b4b24b27-c716-4647-b66d-8b93ead770a5',
                    'provider_auth': None,
                    'project_id': 'project', 'display_name': None,
                    'display_description': 'lun1',
                    'volume_type_id': None}
    volume_clone_large = {'id': 'f6ef5bf5-e24f-4cbb-b4c4-11d631d6e553',
                          'size': 6, 'volume_name': 'lun1',
                          'os_type': 'linux', 'provider_location': 'cl_lg',
                          'name_id': 'f6ef5bf5-e24f-4cbb-b4c4-11d631d6e553',
                          'provider_auth': None,
                          'project_id': 'project', 'display_name': None,
                          'display_description': 'lun1',
                          'volume_type_id': None}
    connector = {'initiator': 'iqn.1998-01.com.vmware:localhost-28a58148'}

    def setUp(self):
        super(NetAppEseriesIscsiDriverTestCase, self).setUp()
        self.configuration = fakes.set_config(fakes.create_configuration())
        self.driver = common.NetAppDriver(configuration=self.configuration)
        requests.Session = mock.Mock(wraps=fakes.FakeEseriesHTTPSession)
        self.driver.do_setup(context='context')
        self.driver.check_for_setup_error()

    def test_embedded_mode(self):
        self.configuration.netapp_controller_ips = '127.0.0.1,127.0.0.3'
        driver = common.NetAppDriver(configuration=self.configuration)
        driver.do_setup(context='context')
        self.assertEqual(driver._client.get_system_id(),
                         '1fa6efb5-f07b-4de4-9f0e-52e5f7ff5d1b')

    def test_check_system_pwd_not_sync(self):
        def list_system():
            if getattr(self, 'test_count', None):
                self.test_count = 1
                return {'status': 'passwordoutofsync'}
            return {'status': 'needsAttention'}

        self.driver._client.list_storage_system = mock.Mock(wraps=list_system)
        result = self.driver._check_storage_system()
        self.assertTrue(result)

    def test_connect(self):
        self.driver.check_for_setup_error()

    def test_create_destroy(self):
        self.driver.create_volume(self.volume)
        self.driver.delete_volume(self.volume)

    def test_create_vol_snapshot_destroy(self):
        self.driver.db = mock.Mock(
            volume_get=mock.Mock(return_value=self.volume))
        self.driver.create_volume(self.volume)
        self.driver.create_snapshot(self.snapshot)
        self.driver.create_volume_from_snapshot(self.volume_sec, self.snapshot)
        self.driver.delete_snapshot(self.snapshot)
        self.driver.delete_volume(self.volume)
        self.assertEqual(1, self.driver.db.volume_get.call_count)

    def test_map_unmap(self):
        self.driver.create_volume(self.volume)
        connection_info = self.driver.initialize_connection(self.volume,
                                                            self.connector)
        self.assertEqual(connection_info['driver_volume_type'], 'iscsi')
        properties = connection_info.get('data')
        self.assertIsNotNone(properties, 'Target portal is none')
        self.driver.terminate_connection(self.volume, self.connector)
        self.driver.delete_volume(self.volume)

    def test_map_already_mapped_same_host(self):
        self.driver.create_volume(self.volume)

        maps = [{'lunMappingRef': 'hdkjsdhjsdh',
                 'mapRef': '8400000060080E500023C73400300381515BFBA3',
                 'volumeRef': '0200000060080E500023BB34000003FB515C2293',
                 'lun': 2}]
        info = self.driver.initialize_connection(self.volume, self.connector)
        self.assertEqual(info['driver_volume_type'], 'iscsi')
        properties = info.get('data')
        self.assertIsNotNone(properties, 'Target portal is none')
        self.driver.terminate_connection(self.volume, self.connector)
        self.driver.delete_volume(self.volume)

    def test_map_already_mapped_diff_host(self):
        self.driver.create_volume(self.volume)

        maps = [{'lunMappingRef': 'hdkjsdhjsdh',
                 'mapRef': '7400000060080E500023C73400300381515BFBA3',
                 'volumeRef': 'CFDXJ67BLJH25DXCZFZD4NSF54',
                 'lun': 2}]
        self.driver._get_vol_mapping_for_host_frm_array = mock.Mock(
            return_value=[])
        info = self.driver.initialize_connection(self.volume, self.connector)
        self.assertEqual(info['driver_volume_type'], 'iscsi')
        properties = info.get('data')
        self.assertIsNotNone(properties, 'Target portal is none')
        self.driver.terminate_connection(self.volume, self.connector)
        self.driver.delete_volume(self.volume)

    def test_cloned_volume_destroy(self):
        self.driver.db = mock.Mock(
            volume_get=mock.Mock(return_value=self.volume))
        self.driver.create_volume(self.volume)
        self.driver.create_cloned_volume(self.volume_sec, self.volume)
        self.assertEqual(1, self.driver.db.volume_get.call_count)
        self.driver.delete_volume(self.volume)

    def test_map_by_creating_host(self):
        self.driver.create_volume(self.volume)
        connector_new = {'initiator': 'iqn.1993-08.org.debian:01:1001'}
        connection_info = self.driver.initialize_connection(self.volume,
                                                            connector_new)
        self.assertEqual(connection_info['driver_volume_type'], 'iscsi')
        properties = connection_info.get('data')
        self.assertIsNotNone(properties, 'Target portal is none')

    def test_vol_stats(self):
        self.driver.get_volume_stats(refresh=True)

    def test_create_vol_snapshot_diff_size_resize(self):
        self.driver.db = mock.Mock(
            volume_get=mock.Mock(return_value=self.volume))
        self.driver.create_volume(self.volume)
        self.driver.create_snapshot(self.snapshot)
        self.driver.create_volume_from_snapshot(
            self.volume_clone, self.snapshot)
        self.assertEqual(1, self.driver.db.volume_get.call_count)
        self.driver.delete_snapshot(self.snapshot)
        self.driver.delete_volume(self.volume)

    def test_create_vol_snapshot_diff_size_subclone(self):
        self.driver.db = mock.Mock(
            volume_get=mock.Mock(return_value=self.volume))
        self.driver.create_volume(self.volume)
        self.driver.create_snapshot(self.snapshot)
        self.driver.create_volume_from_snapshot(
            self.volume_clone_large, self.snapshot)
        self.driver.delete_snapshot(self.snapshot)
        self.assertEqual(1, self.driver.db.volume_get.call_count)
        self.driver.delete_volume(self.volume)

    def test_get_host_right_type(self):
        self.driver._get_host_with_initiator = mock.Mock(
            return_value={'hostTypeIndex': 2, 'name': 'test'})
        self.driver._client.get_host_type = mock.Mock(
            return_value={'index': 2, 'name': 'LnxALUA'})
        host = self.driver._get_or_create_host('port', 'LnxALUA')
        self.assertEqual(host, {'hostTypeIndex': 2, 'name': 'test'})
        self.driver._get_host_with_initiator.assert_called_once_with('port')

    def test_get_host_not_found(self):
        self.driver._get_host_with_initiator = mock.Mock(
            side_effect=exception.NotFound)
        self.driver._create_host = mock.Mock()
        self.driver._get_or_create_host('port', 'LnxALUA')
        self.driver._get_host_with_initiator.assert_called_once_with('port')
        self.driver._create_host.assert_called_once_with('port', 'LnxALUA')

    def test_setup_error_unsupported_host_type(self):
        self.configuration.netapp_eseries_host_type = 'garbage'
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.NetAppDriverException,
                          driver.check_for_setup_error)

    def test_setup_good_controller_ip(self):
        self.configuration.netapp_controller_ips = '127.0.0.1'
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system

    def test_setup_good_controller_ips(self):
        self.configuration.netapp_controller_ips = '127.0.0.2,127.0.0.1'
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system

    def test_setup_missing_controller_ip(self):
        self.configuration.netapp_controller_ips = None
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.InvalidInput,
                          driver.do_setup, context='context')

    def test_setup_error_invalid_controller_ip(self):
        self.configuration.netapp_controller_ips = '987.65.43.21'
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.NoValidHost,
                          driver._check_mode_get_or_register_storage_system)

    def test_setup_error_invalid_first_controller_ip(self):
        self.configuration.netapp_controller_ips = '987.65.43.21,127.0.0.1'
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.NoValidHost,
                          driver._check_mode_get_or_register_storage_system)

    def test_setup_error_invalid_second_controller_ip(self):
        self.configuration.netapp_controller_ips = '127.0.0.1,987.65.43.21'
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.NoValidHost,
                          driver._check_mode_get_or_register_storage_system)

    def test_setup_error_invalid_both_controller_ips(self):
        self.configuration.netapp_controller_ips = ('564.124.1231.1,'
                                                    '987.65.43.21')
        driver = common.NetAppDriver(configuration=self.configuration)
        self.assertRaises(exception.NoValidHost,
                          driver._check_mode_get_or_register_storage_system)

    def test_do_setup_all_default(self):
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system = mock.Mock()
        driver.do_setup(context='context')
        url = urlparse.urlparse(driver._client._endpoint)
        port = url.port
        scheme = url.scheme
        self.assertEqual(8080, port)
        self.assertEqual('http', scheme)

    def test_do_setup_http_default_port(self):
        self.configuration.netapp_transport_type = 'http'
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system = mock.Mock()
        driver.do_setup(context='context')
        url = urlparse.urlparse(driver._client._endpoint)
        port = url.port
        scheme = url.scheme
        self.assertEqual(8080, port)
        self.assertEqual('http', scheme)

    def test_do_setup_https_default_port(self):
        self.configuration.netapp_transport_type = 'https'
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system = mock.Mock()
        driver.do_setup(context='context')
        url = urlparse.urlparse(driver._client._endpoint)
        port = url.port
        scheme = url.scheme
        self.assertEqual(8443, port)
        self.assertEqual('https', scheme)

    def test_do_setup_http_non_default_port(self):
        self.configuration.netapp_server_port = 81
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system = mock.Mock()
        driver.do_setup(context='context')
        url = urlparse.urlparse(driver._client._endpoint)
        port = url.port
        scheme = url.scheme
        self.assertEqual(81, port)
        self.assertEqual('http', scheme)

    def test_do_setup_https_non_default_port(self):
        self.configuration.netapp_transport_type = 'https'
        self.configuration.netapp_server_port = 446
        driver = common.NetAppDriver(configuration=self.configuration)
        driver._check_mode_get_or_register_storage_system = mock.Mock()
        driver.do_setup(context='context')
        url = urlparse.urlparse(driver._client._endpoint)
        port = url.port
        scheme = url.scheme
        self.assertEqual(446, port)
        self.assertEqual('https', scheme)
