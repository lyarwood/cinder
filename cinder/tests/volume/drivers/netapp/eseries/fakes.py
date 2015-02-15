# Copyright (c) - 2015, Alex Meade
# Copyright (c) - 2015, Yogesh Kshirsagar
#  All Rights Reserved.
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


from cinder.volume import configuration as conf
import cinder.volume.drivers.netapp.options as na_opts


NULL_REF = '0000000000000000000000000000000000000000'
STORAGE_POOL = {
    'label': 'DDP',
    'volumeGroupRef': 'fakevolgroupref',
    'raidLevel': 'raidDiskPool',
}

VOLUME = {
    'extremeProtection': False,
    'pitBaseVolume': True,
    'dssMaxSegmentSize': 131072,
    'totalSizeInBytes': '1073741824',
    'raidLevel': 'raid6',
    'volumeRef': '0200000060080E500023BB34000003FB515C2293',
    'listOfMappings': [],
    'sectorOffset': '15',
    'id': '0200000060080E500023BB34000003FB515C2293',
    'wwn': '60080E500023BB3400001FC352D14CB2',
    'capacity': '2147483648',
    'mgmtClientAttribute': 0,
    'label': 'CFDXJ67BLJH25DXCZFZD4NSF54',
    'volumeFull': False,
    'blkSize': 512,
    'volumeCopyTarget': False,
    'volumeGroupRef': '0400000060080E500023BB3400001F9F52CECC3F',
    'preferredControllerId': '070000000000000000000001',
    'currentManager': '070000000000000000000001',
    'applicationTagOwned': False,
    'status': 'optimal',
    'segmentSize': 131072,
    'volumeUse': 'standardVolume',
    'action': 'none',
    'preferredManager': '070000000000000000000001',
    'volumeHandle': 15,
    'offline': False,
    'preReadRedundancyCheckEnabled': False,
    'dssPreallocEnabled': False,
    'name': 'bdm-vc-test-1',
    'worldWideName': '60080E500023BB3400001FC352D14CB2',
    'currentControllerId': '070000000000000000000001',
    'protectionInformationCapable': False,
    'mapped': False,
    'reconPriority': 1,
    'protectionType': 'type1Protection'
}

INITIATOR_NAME = 'iqn.1998-01.com.vmware:localhost-28a58148'
INITIATOR_NAME_2 = 'iqn.1998-01.com.vmware:localhost-28a58149'
INITIATOR_NAME_3 = 'iqn.1998-01.com.vmware:localhost-28a58150'
WWPN = '20130080E5322230'
WWPN_2 = '20230080E5322230'

FC_TARGET_WWPNS = [
    '500a098280feeba5',
    '500a098290feeba5',
    '500a098190feeba5',
    '500a098180feeba5'
]

FC_I_T_MAP = {
    '20230080E5322230': [
        '500a098280feeba5',
        '500a098290feeba5'
    ],
    '20130080E5322230': [
        '500a098190feeba5',
        '500a098180feeba5'
    ]
}

FC_FABRIC_MAP = {
    'fabricB': {
        'target_port_wwn_list': [
            '500a098190feeba5',
            '500a098180feeba5'
        ],
        'initiator_port_wwn_list': [
            '20130080E5322230'
        ]
    },
    'fabricA': {
        'target_port_wwn_list': [
            '500a098290feeba5',
            '500a098280feeba5'
        ],
        'initiator_port_wwn_list': [
            '20230080E5322230'
        ]
    }
}

HOST = {
    'isSAControlled': False,
    'confirmLUNMappingCreation': False,
    'label': 'stlrx300s7-55',
    'isLargeBlockFormatHost': False,
    'clusterRef': '8500000060080E500023C7340036035F515B78FC',
    'protectionInformationCapableAccessMethod': False,
    'ports': [],
    'hostRef': '8400000060080E500023C73400300381515BFBA3',
    'hostTypeIndex': 6,
    'hostSidePorts': [{
        'label': 'NewStore',
        'type': 'iscsi',
        'address': INITIATOR_NAME}]
}
HOST_2 = {
    'isSAControlled': False,
    'confirmLUNMappingCreation': False,
    'label': 'stlrx300s7-55',
    'isLargeBlockFormatHost': False,
    'clusterRef': NULL_REF,
    'protectionInformationCapableAccessMethod': False,
    'ports': [],
    'hostRef': '8400000060080E500023C73400300381515BFBA5',
    'hostTypeIndex': 6,
    'hostSidePorts': [{
        'label': 'NewStore', 'type': 'iscsi',
        'address': INITIATOR_NAME_2}]
}
HOST_TYPES = [
    {
        'id': '4',
        'code': 'AIX',
        'name': 'AIX',
        'index': 4
    },
    {
        'id': '5',
        'code': 'IRX',
        'name': 'IRX',
        'index': 5
    },
    {
        'id': '6',
        'code': 'LnxALUA',
        'name': 'LnxALUA',
        'index': 6
    }
]

VOLUME_MAPPING = {
    'lunMappingRef': '8800000000000000000000000000000000000000',
    'lun': 0,
    'ssid': 16384,
    'perms': 15,
    'volumeRef': VOLUME['volumeRef'],
    'type': 'all',
    'mapRef': HOST['hostRef']
}


STORAGE_SYSTEM = {
    'freePoolSpace': 11142431623168,
    'driveCount': 24,
    'hostSparesUsed': 0, 'id':
    '1fa6efb5-f07b-4de4-9f0e-52e5f7ff5d1b',
    'hotSpareSizeAsString': '0', 'wwn':
    '60080E500023C73400000000515AF323',
    'parameters': {
        'minVolSize': 1048576, 'maxSnapshotsPerBase': 16,
        'maxDrives': 192,
        'maxVolumes': 512,
        'maxVolumesPerGroup': 256,
        'maxMirrors': 0,
        'maxMappingsPerVolume': 1,
        'maxMappableLuns': 256,
        'maxVolCopys': 511,
        'maxSnapshots': 256
    }, 'hotSpareCount': 0,
    'hostSpareCountInStandby': 0,
    'status': 'needsattn',
    'trayCount': 1,
    'usedPoolSpaceAsString': '5313000380416',
    'ip2': '10.63.165.216',
    'ip1': '10.63.165.215',
    'freePoolSpaceAsString': '11142431623168',
    'types': 'SAS',
    'name': 'stle2600-7_8',
    'hotSpareSize': 0,
    'usedPoolSpace': 5313000380416,
    'driveTypes': ['sas'],
    'unconfiguredSpaceByDriveType': {},
    'unconfiguredSpaceAsStrings': '0',
    'model': '2650',
    'unconfiguredSpace': 0
}

SNAPSHOT_GROUP = {
    'status': 'optimal',
    'autoDeleteLimit': 0,
    'maxRepositoryCapacity': '-65536',
    'rollbackStatus': 'none',
    'unusableRepositoryCapacity': '0',
    'pitGroupRef':
    '3300000060080E500023C7340000098D5294AC9A',
    'clusterSize': 65536,
    'label': 'C6JICISVHNG2TFZX4XB5ZWL7O',
    'maxBaseCapacity': '476187142128128',
    'repositoryVolume': '3600000060080E500023BB3400001FA952CEF12C',
    'fullWarnThreshold': 99,
    'repFullPolicy': 'purgepit',
    'action': 'none',
    'rollbackPriority': 'medium',
    'creationPendingStatus': 'none',
    'consistencyGroupRef': '0000000000000000000000000000000000000000',
    'volumeHandle': 49153,
    'consistencyGroup': False,
    'baseVolume': '0200000060080E500023C734000009825294A534'
}

SNAPSHOT_IMAGE = {
    'status': 'optimal',
    'pitCapacity': '2147483648',
    'pitTimestamp': '1389315375',
    'pitGroupRef': '3300000060080E500023C7340000098D5294AC9A',
    'creationMethod': 'user',
    'repositoryCapacityUtilization': '2818048',
    'activeCOW': True,
    'isRollbackSource': False,
    'pitRef': '3400000060080E500023BB3400631F335294A5A8',
    'pitSequenceNumber': '19'
}

HARDWARE_INVENTORY = {
    'iscsiPorts': [
        {
            'controllerId':
            '070000000000000000000002',
            'ipv4Enabled': True,
            'ipv4Data': {
                'ipv4Address': '0.0.0.0',
                'ipv4AddressConfigMethod':
                'configStatic',
                'ipv4VlanId': {
                    'isEnabled': False,
                    'value': 0
                },
                'ipv4AddressData': {
                    'ipv4Address': '172.20.123.66',
                    'ipv4SubnetMask': '255.255.255.0',
                    'configState': 'configured',
                    'ipv4GatewayAddress': '0.0.0.0'
                }
            },
            'tcpListenPort': 3260,
            'interfaceRef': '2202040000000000000000000000000000000000',
            'iqn': 'iqn.1992-01.com.lsi:2365.60080e500023c73400000000515af323'
        }
    ],
    'fibrePorts': [
        {
            "channel": 1,
            "loopID": 126,
            "speed": 800,
            "hardAddress": 6,
            "nodeName": "20020080E5322230",
            "portName": "20130080E5322230",
            "portId": "011700",
            "topology": "fabric",
            "part": "PM8032          ",
            "revision": 8,
            "chanMiswire": False,
            "esmMiswire": False,
            "linkStatus": "up",
            "isDegraded": False,
            "speedControl": "auto",
            "maxSpeed": 800,
            "speedNegError": False,
            "reserved1": "000000000000000000000000",
            "reserved2": "",
            "ddsChannelState": 0,
            "ddsStateReason": 0,
            "ddsStateWho": 0,
            "isLocal": True,
            "channelPorts": [],
            "currentInterfaceSpeed": "speed8gig",
            "maximumInterfaceSpeed": "speed8gig",
            "interfaceRef": "2202020000000000000000000000000000000000",
            "physicalLocation": {
                "trayRef": "0000000000000000000000000000000000000000",
                "slot": 0,
                "locationParent": {
                    "refType": "generic",
                    "controllerRef": None,
                    "symbolRef": "0000000000000000000000000000000000000000",
                    "typedReference": None
                },
                "locationPosition": 0
            },
            "isTrunkCapable": False,
            "trunkMiswire": False,
            "protectionInformationCapable": True,
            "controllerId": "070000000000000000000002",
            "interfaceId": "2202020000000000000000000000000000000000",
            "addressId": "20130080E5322230",
            "niceAddressId": "20:13:00:80:E5:32:22:30"
        },
        {
            "channel": 2,
            "loopID": 126,
            "speed": 800,
            "hardAddress": 7,
            "nodeName": "20020080E5322230",
            "portName": "20230080E5322230",
            "portId": "011700",
            "topology": "fabric",
            "part": "PM8032          ",
            "revision": 8,
            "chanMiswire": False,
            "esmMiswire": False,
            "linkStatus": "up",
            "isDegraded": False,
            "speedControl": "auto",
            "maxSpeed": 800,
            "speedNegError": False,
            "reserved1": "000000000000000000000000",
            "reserved2": "",
            "ddsChannelState": 0,
            "ddsStateReason": 0,
            "ddsStateWho": 0,
            "isLocal": True,
            "channelPorts": [],
            "currentInterfaceSpeed": "speed8gig",
            "maximumInterfaceSpeed": "speed8gig",
            "interfaceRef": "2202030000000000000000000000000000000000",
            "physicalLocation": {
                "trayRef": "0000000000000000000000000000000000000000",
                "slot": 0,
                "locationParent": {
                    "refType": "generic",
                    "controllerRef": None,
                    "symbolRef": "0000000000000000000000000000000000000000",
                    "typedReference": None
                },
                "locationPosition": 0
            },
            "isTrunkCapable": False,
            "trunkMiswire": False,
            "protectionInformationCapable": True,
            "controllerId": "070000000000000000000002",
            "interfaceId": "2202030000000000000000000000000000000000",
            "addressId": "20230080E5322230",
            "niceAddressId": "20:23:00:80:E5:32:22:30"
        },
    ]
}


VOLUME_COPY_JOB = {
    "status": "complete",
    "cloneCopy": True,
    "pgRef": "3300000060080E500023C73400000ACA52D29454",
    "volcopyHandle": 49160,
    "idleTargetWriteProt": True,
    "copyPriority": "priority2",
    "volcopyRef": "1800000060080E500023C73400000ACF52D29466",
    "worldWideName": "60080E500023C73400000ACF52D29466",
    "copyCompleteTime": "0",
    "sourceVolume": "3500000060080E500023C73400000ACE52D29462",
    "currentManager": "070000000000000000000002",
    "copyStartTime": "1389551671",
    "reserved1": "00000000",
    "targetVolume": "0200000060080E500023C73400000A8C52D10675",
}


def create_configuration_eseries():
    config = conf.Configuration(None)
    config.append_config_values(na_opts.netapp_connection_opts)
    config.append_config_values(na_opts.netapp_transport_opts)
    config.append_config_values(na_opts.netapp_basicauth_opts)
    config.append_config_values(na_opts.netapp_provisioning_opts)
    config.append_config_values(na_opts.netapp_eseries_opts)
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
    config.netapp_enable_multiattach = False
    return config
