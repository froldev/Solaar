# -*- python-mode -*-
# -*- coding: UTF-8 -*-

## Copyright (C) 2012-2013  Daniel Pavel
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Logitech Unifying Receiver API.

from __future__ import absolute_import, division, print_function, unicode_literals

from logging import DEBUG as _DEBUG
from logging import ERROR as _ERROR
from logging import WARNING as _WARNING
from logging import getLogger
from typing import List

from . import special_keys
from .common import FirmwareInfo as _FirmwareInfo
from .common import KwException as _KwException
from .common import NamedInt as _NamedInt
from .common import NamedInts as _NamedInts
from .common import pack as _pack
from .common import unpack as _unpack

_log = getLogger(__name__)
del getLogger

#
#
#

# <FeaturesSupported.xml sed '/LD_FID_/{s/.*LD_FID_/\t/;s/"[ \t]*Id="/=/;s/" \/>/,/p}' | sort -t= -k2
# additional features names taken from https://github.com/cvuchener/hidpp and
# https://github.com/Logitech/cpg-docs/tree/master/hidpp20
"""Possible features available on a Logitech device.

A particular device might not support all these features, and may support other
unknown features as well.
"""
FEATURE = _NamedInts(
    ROOT=0x0000,
    FEATURE_SET=0x0001,
    FEATURE_INFO=0x0002,
    # Common
    DEVICE_FW_VERSION=0x0003,
    DEVICE_UNIT_ID=0x0004,
    DEVICE_NAME=0x0005,
    DEVICE_GROUPS=0x0006,
    DEVICE_FRIENDLY_NAME=0x0007,
    KEEP_ALIVE=0x0008,
    RESET=0x0020,  # "Config Change"
    CRYPTO_ID=0x0021,
    TARGET_SOFTWARE=0x0030,
    WIRELESS_SIGNAL_STRENGTH=0x0080,
    DFUCONTROL_LEGACY=0x00C0,
    DFUCONTROL_UNSIGNED=0x00C1,
    DFUCONTROL_SIGNED=0x00C2,
    DFU=0x00D0,
    BATTERY_STATUS=0x1000,
    BATTERY_VOLTAGE=0x1001,
    CHARGING_CONTROL=0x1010,
    LED_CONTROL=0x1300,
    GENERIC_TEST=0x1800,
    DEVICE_RESET=0x1802,
    OOBSTATE=0x1805,
    CONFIG_DEVICE_PROPS=0x1806,
    CHANGE_HOST=0x1814,
    HOSTS_INFO=0x1815,
    BACKLIGHT=0x1981,
    BACKLIGHT2=0x1982,
    BACKLIGHT3=0x1983,
    PRESENTER_CONTROL=0x1A00,
    SENSOR_3D=0x1A01,
    REPROG_CONTROLS=0x1B00,
    REPROG_CONTROLS_V2=0x1B01,
    REPROG_CONTROLS_V2_2=0x1B02,  # LogiOptions 2.10.73 features.xml
    REPROG_CONTROLS_V3=0x1B03,
    REPROG_CONTROLS_V4=0x1B04,
    REPORT_HID_USAGE=0x1BC0,
    PERSISTENT_REMAPPABLE_ACTION=0x1C00,
    WIRELESS_DEVICE_STATUS=0x1D4B,
    REMAINING_PAIRING=0x1DF0,
    FIRMWARE_PROPERTIES=0x1F1F,
    ADC_MEASUREMENT=0x1F20,
    # Mouse
    LEFT_RIGHT_SWAP=0x2001,
    SWAP_BUTTON_CANCEL=0x2005,
    POINTER_AXIS_ORIENTATION=0x2006,
    VERTICAL_SCROLLING=0x2100,
    SMART_SHIFT=0x2110,
    HI_RES_SCROLLING=0x2120,
    HIRES_WHEEL=0x2121,
    LOWRES_WHEEL=0x2130,
    THUMB_WHEEL=0x2150,
    MOUSE_POINTER=0x2200,
    ADJUSTABLE_DPI=0x2201,
    POINTER_SPEED=0x2205,
    ANGLE_SNAPPING=0x2230,
    SURFACE_TUNING=0x2240,
    HYBRID_TRACKING=0x2400,
    # Keyboard
    FN_INVERSION=0x40A0,
    NEW_FN_INVERSION=0x40A2,
    K375S_FN_INVERSION=0x40A3,
    ENCRYPTION=0x4100,
    LOCK_KEY_STATE=0x4220,
    SOLAR_DASHBOARD=0x4301,
    KEYBOARD_LAYOUT=0x4520,
    KEYBOARD_DISABLE_KEYS=0x4521,
    KEYBOARD_DISABLE_BY_USAGE=0x4522,
    DUALPLATFORM=0x4530,
    MULTIPLATFORM=0x4531,
    KEYBOARD_LAYOUT_2=0x4540,
    CROWN=0x4600,
    # Touchpad
    TOUCHPAD_FW_ITEMS=0x6010,
    TOUCHPAD_SW_ITEMS=0x6011,
    TOUCHPAD_WIN8_FW_ITEMS=0x6012,
    TAP_ENABLE=0x6020,
    TAP_ENABLE_EXTENDED=0x6021,
    CURSOR_BALLISTIC=0x6030,
    TOUCHPAD_RESOLUTION=0x6040,
    TOUCHPAD_RAW_XY=0x6100,
    TOUCHMOUSE_RAW_POINTS=0x6110,
    TOUCHMOUSE_6120=0x6120,
    GESTURE=0x6500,
    GESTURE_2=0x6501,
    # Gaming Devices
    GKEY=0x8010,
    MKEYS=0x8020,
    MR=0x8030,
    BRIGHTNESS_CONTROL=0x8040,
    REPORT_RATE=0x8060,
    COLOR_LED_EFFECTS=0x8070,
    RGB_EFFECTS=0x8071,
    PER_KEY_LIGHTING=0x8080,
    PER_KEY_LIGHTING_V2=0x8081,
    MODE_STATUS=0x8090,
    ONBOARD_PROFILES=0x8100,
    MOUSE_BUTTON_SPY=0x8110,
    LATENCY_MONITORING=0x8111,
    GAMING_ATTACHMENTS=0x8120,
    FORCE_FEEDBACK=0x8123,
    SIDETONE=0x8300,
    EQUALIZER=0x8310,
    HEADSET_OUT=0x8320,
)
FEATURE._fallback = lambda x: 'unknown:%04X' % x

FEATURE_FLAG = _NamedInts(internal=0x20, hidden=0x40, obsolete=0x80)

DEVICE_KIND = _NamedInts(
    keyboard=0x00, remote_control=0x01, numpad=0x02, mouse=0x03, touchpad=0x04, trackball=0x05, presenter=0x06, receiver=0x07
)

FIRMWARE_KIND = _NamedInts(Firmware=0x00, Bootloader=0x01, Hardware=0x02, Other=0x03)

BATTERY_OK = lambda status: status not in (BATTERY_STATUS.invalid_battery, BATTERY_STATUS.thermal_error)

BATTERY_STATUS = _NamedInts(
    discharging=0x00,
    recharging=0x01,
    almost_full=0x02,
    full=0x03,
    slow_recharge=0x04,
    invalid_battery=0x05,
    thermal_error=0x06
)

CHARGE_STATUS = _NamedInts(charging=0x00, full=0x01, not_charging=0x02, error=0x07)

CHARGE_LEVEL = _NamedInts(average=50, full=90, critical=5)

CHARGE_TYPE = _NamedInts(standard=0x00, fast=0x01, slow=0x02)

ERROR = _NamedInts(
    unknown=0x01,
    invalid_argument=0x02,
    out_of_range=0x03,
    hardware_error=0x04,
    logitech_internal=0x05,
    invalid_feature_index=0x06,
    invalid_function=0x07,
    busy=0x08,
    unsupported=0x09
)

#
#
#


class FeatureNotSupported(_KwException):
    """Raised when trying to request a feature not supported by the device."""
    pass


class FeatureCallError(_KwException):
    """Raised if the device replied to a feature call with an error."""
    pass


#
#
#


class FeaturesArray(object):
    """A sequence of features supported by a HID++ 2.0 device."""
    __slots__ = ('supported', 'device', 'features', 'non_features')
    assert FEATURE.ROOT == 0x0000

    def __init__(self, device):
        assert device is not None
        self.device = device
        self.supported = True
        self.features = None
        self.non_features = set()

    def __del__(self):
        self.supported = False
        self.device = None
        self.features = None

    def _check(self):
        # print (self.device, "check", self.supported, self.features, self.device.protocol)
        if self.supported:
            assert self.device is not None
            if self.features is not None:
                return True

            if not self.device.online:
                # device is not connected right now, will have to try later
                return False

            # I _think_ this is universally true
            if self.device.protocol and self.device.protocol < 2.0:
                self.supported = False
                self.device.features = None
                self.device = None
                return False

            reply = self.device.request(0x0000, _pack('!H', FEATURE.FEATURE_SET))
            if reply is None:
                self.supported = False
            else:
                fs_index = ord(reply[0:1])
                if fs_index:
                    count = self.device.request(fs_index << 8)
                    if count is None:
                        _log.warn('FEATURE_SET found, but failed to read features count')
                        # most likely the device is unavailable
                        return False
                    else:
                        count = ord(count[:1])
                        assert count >= fs_index
                        self.features = [None] * (1 + count)
                        self.features[0] = FEATURE.ROOT
                        self.features[fs_index] = FEATURE.FEATURE_SET
                        return True
                else:
                    self.supported = False

        return False

    __bool__ = __nonzero__ = _check

    def __getitem__(self, index):
        if self._check():
            if isinstance(index, int):
                if index < 0 or index >= len(self.features):
                    raise IndexError(index)

                if self.features[index] is None:
                    feature = self.device.feature_request(FEATURE.FEATURE_SET, 0x10, index)
                    if feature:
                        feature, = _unpack('!H', feature[:2])
                        self.features[index] = FEATURE[feature]

                return self.features[index]

            elif isinstance(index, slice):
                indices = index.indices(len(self.features))
                return [self.__getitem__(i) for i in range(*indices)]

    def __contains__(self, featureId):
        """Tests whether the list contains given Feature ID"""
        if self._check():
            ivalue = int(featureId)
            if ivalue in self.non_features:
                return False

            may_have = False
            for f in self.features:
                if f is None:
                    may_have = True
                elif ivalue == int(f):
                    return True

            if may_have:
                reply = self.device.request(0x0000, _pack('!H', ivalue))
                if reply:
                    index = ord(reply[0:1])
                    if index:
                        self.features[index] = FEATURE[ivalue]
                        return True
                    else:
                        self.non_features.add(ivalue)
                        return False

    def index(self, featureId):
        """Gets the Feature Index for a given Feature ID"""
        if self._check():
            may_have = False
            ivalue = int(featureId)
            for index, f in enumerate(self.features):
                if f is None:
                    may_have = True
                elif ivalue == int(f):
                    return index

            if may_have:
                reply = self.device.request(0x0000, _pack('!H', ivalue))
                if reply:
                    index = ord(reply[0:1])
                    self.features[index] = FEATURE[ivalue]
                    return index

        raise ValueError('%r not in list' % featureId)

    def __iter__(self):
        if self._check():
            yield FEATURE.ROOT
            index = 1
            last_index = len(self.features)
            while index < last_index:
                yield self.__getitem__(index)
                index += 1

    def __len__(self):
        return len(self.features) if self._check() else 0


#
#
#


class ReprogrammableKey(object):
    """Information about a control present on a device with the `REPROG_CONTROLS` feature.
    Ref: https://drive.google.com/file/d/0BxbRzx7vEV7eU3VfMnRuRXktZ3M/view
    Read-only properties:
    - index {int} -- index in the control ID table
    - key {_NamedInt} -- the name of this control
    - default_task {_NamedInt} -- the native function of this control
    - flags {List[str]} -- capabilities and desired software handling of the control
    """
    def __init__(self, device, index, cid, tid, flags):
        self._device = device
        self.index = index
        self._cid = cid
        self._tid = tid
        self._flags = flags

    @property
    def key(self) -> _NamedInt:
        return special_keys.CONTROL[self._cid]

    @property
    def default_task(self) -> _NamedInt:
        """NOTE: This NamedInt is a bit mixed up, because its value is the Control ID
        while the name is the Control ID's native task. But this makes more sense
        than presenting details of controls vs tasks in the interface. The same
        convention applies to `mapped_to`, `remappable_to`, `remap` in `ReprogrammableKeyV4`."""
        task = str(special_keys.TASK[self._tid])
        return _NamedInt(self._cid, task)

    @property
    def flags(self) -> List[str]:
        return special_keys.KEY_FLAG.flag_names(self._flags)


class ReprogrammableKeyV4(ReprogrammableKey):
    """Information about a control present on a device with the `REPROG_CONTROLS_V4` feature.
    Ref (v2): https://lekensteyn.nl/files/logitech/x1b04_specialkeysmsebuttons.html
    Ref (v4): https://drive.google.com/file/d/10imcbmoxTJ1N510poGdsviEhoFfB_Ua4/view
    Contains all the functionality of `ReprogrammableKey` plus remapping keys and /diverting/ them
    in order to handle keypresses in a custom way.

    Additional read-only properties:
    - pos {int} -- position of this control on the device; 1-16 for FN-keys, otherwise 0
    - group {int} -- the group this control belongs to; other controls with this group in their
    `group_mask` can be remapped to this control
    - group_mask {List[str]} -- this control can be remapped to any control ID in these groups
    - mapped_to {_NamedInt} -- which action this control is mapped to; usually itself
    - remappable_to {List[_NamedInt]} -- list of actions which this control can be remapped to
    - mapping_flags {List[str]} -- mapping flags set on the control
    """
    def __init__(self, device, index, cid, tid, flags, pos, group, gmask):
        ReprogrammableKey.__init__(self, device, index, cid, tid, flags)
        self.pos = pos
        self.group = group
        self._gmask = gmask
        self._mapping_flags = None
        self._mapped_to = None

    @property
    def group_mask(self):
        return special_keys.CID_GROUP_BIT.flag_names(self._gmask)

    @property
    def mapped_to(self) -> _NamedInt:
        if self._mapped_to is None:
            self._getCidReporting()
        self._device.keys._ensure_all_keys_queried()
        task = str(special_keys.TASK[self._device.keys.cid_to_tid[self._mapped_to]])
        return _NamedInt(self._mapped_to, task)

    @property
    def remappable_to(self) -> List[_NamedInt]:
        # this flag is only to show in UI, ignore in Solaar
        # if special_keys.KEY_FLAG.reprogrammable not in self.flags:
        #     return []

        self._device.keys._ensure_all_keys_queried()
        ret = []
        if self.group_mask != []:  # only keys with a non-zero gmask are remappable
            ret = [self.default_task]  # it should always be possible to map the key to itself
            for g in self.group_mask:
                g = special_keys.CID_GROUP[str(g)]
                for tgt_cid in self._device.keys.group_cids[g]:
                    tgt_task = str(special_keys.TASK[self._device.keys.cid_to_tid[tgt_cid]])
                    tgt_task = _NamedInt(tgt_cid, tgt_task)
                    if tgt_task != self.default_task:  # don't put itself in twice
                        ret.append(tgt_task)

        return ret

    @property
    def mapping_flags(self) -> List[str]:
        if self._mapping_flags is None:
            self._getCidReporting()
        return special_keys.MAPPING_FLAG.flag_names(self._mapping_flags)

    def set_diverted(self, value: bool):
        """If set, the control is diverted temporarily and reports presses as HID++ events
        until a HID++ configuration reset occurs."""
        flags = {special_keys.MAPPING_FLAG.diverted: value}
        self._setCidReporting(flags=flags)

    def set_persistently_diverted(self, value: bool):
        """If set, the control is diverted permanently and reports presses as HID++ events."""
        flags = {special_keys.MAPPING_FLAG.persistently_diverted: value}
        self._setCidReporting(flags=flags)

    def set_rawXY_reporting(self, value: bool):
        """If set, the mouse reports all its raw XY events while this control is pressed
        as HID++ events. Gets cleared on a HID++ configuration reset."""
        flags = {special_keys.MAPPING_FLAG.raw_XY_diverted: value}
        self._setCidReporting(flags=flags)

    def remap(self, to: _NamedInt):
        """Remaps this control to another action."""
        self._setCidReporting(remap=int(to))

    def _getCidReporting(self):
        try:
            mapped_data = feature_request(
                self._device,
                FEATURE.REPROG_CONTROLS_V4,
                0x20,
                *tuple(_pack('!H', self._cid)),
            )
            if mapped_data:
                cid, mapping_flags_1, mapped_to = _unpack('!HBH', mapped_data[:5])
                if cid != self._cid and _log.isEnabledFor(_WARNING):
                    _log.warn(
                        f'REPROG_CONTROLS_V4 endpoint getCidReporting on device {self._device} replied ' +
                        f'with a different control ID ({cid}) than requested ({self._cid}).'
                    )
                self._mapped_to = mapped_to if mapped_to != 0 else self._cid
                if len(mapped_data) > 5:
                    mapping_flags_2, = _unpack('!B', mapped_data[5:6])
                else:
                    mapping_flags_2 = 0
                self._mapping_flags = mapping_flags_1 | (mapping_flags_2 << 8)
            else:
                raise FeatureCallError(msg='No reply from device.')
        except Exception:
            if _log.isEnabledFor(_ERROR):
                _log.error(f'Exception in _getCidReporting on device {self._device}: ', exc_info=1)
            # Clear flags and set mapping target to self as fallback
            self._mapping_flags = 0
            self._mapped_to = self._cid

    def _setCidReporting(self, flags=None, remap=0):
        """Sends a `setCidReporting` request with the given parameters to the control. Raises
        an exception if the parameters are invalid.

        Parameters:
        - flags {Dict[_NamedInt,bool]} -- a dictionary of which mapping flags to set/unset
        - remap {int} -- which control ID to remap to; or 0 to keep current mapping
        """
        flags = flags if flags else {}  # See flake8 B006

        if special_keys.MAPPING_FLAG.raw_XY_diverted in flags and flags[special_keys.MAPPING_FLAG.raw_XY_diverted]:
            # We need diversion to report raw XY, so divert temporarily
            # (since XY reporting is also temporary)
            flags[special_keys.MAPPING_FLAG.diverted] = True

        if special_keys.MAPPING_FLAG.diverted in flags and not flags[special_keys.MAPPING_FLAG.diverted]:
            flags[special_keys.MAPPING_FLAG.raw_XY_diverted] = False

        # The capability required to set a given reporting flag.
        FLAG_TO_CAPABILITY = {
            special_keys.MAPPING_FLAG.diverted: special_keys.KEY_FLAG.divertable,
            special_keys.MAPPING_FLAG.persistently_diverted: special_keys.KEY_FLAG.persistently_divertable,
            special_keys.MAPPING_FLAG.analytics_key_events_reporting: special_keys.KEY_FLAG.analytics_key_events,
            special_keys.MAPPING_FLAG.force_raw_XY_diverted: special_keys.KEY_FLAG.force_raw_XY,
            special_keys.MAPPING_FLAG.raw_XY_diverted: special_keys.KEY_FLAG.raw_XY
        }

        bfield = 0
        for f, v in flags.items():
            if v and FLAG_TO_CAPABILITY[f] not in self.flags:
                raise FeatureNotSupported(
                    msg=f'Tried to set mapping flag "{f}" on control "{self.key}" ' +
                    f'which does not support "{FLAG_TO_CAPABILITY[f]}" on device {self._device}.'
                )

            bfield |= int(f) if v else 0
            bfield |= int(f) << 1  # The 'Xvalid' bit

        if remap != 0 and remap not in self.remappable_to:
            raise FeatureNotSupported(
                msg=f'Tried to remap control "{self.key}" to a control ID {remap} which it is not remappable to ' +
                f'on device {self._device}.'
            )

        pkt = tuple(
            _pack(
                '!HBH',
                self._cid,
                bfield & 0xff,
                remap,
                # TODO: to fully support version 4 of REPROG_CONTROLS_V4, append
                # another byte `(bfield >> 8) & 0xff` here. But older devices
                # might behave oddly given that byte, so we don't send it.
            )
        )
        ret = feature_request(self._device, FEATURE.REPROG_CONTROLS_V4, 0x30, *pkt)
        if _unpack('!BBBBB', ret[:5]) != pkt and _log.isEnabledFor(_WARNING):
            _log.warn(
                f"REPROG_CONTROLS_v4 endpoint setCidReporting on device {self._device} should echo request packet, but didn't."
            )

        # update knowledge of mapping
        self._getCidReporting()


class KeysArray(object):
    """A sequence of key mappings supported by a HID++ 2.0 device."""

    __slots__ = ('device', 'keys', 'keyversion', 'cid_to_tid', 'group_cids')

    def __init__(self, device, count):
        assert device is not None
        self.device = device
        if FEATURE.REPROG_CONTROLS in self.device.features:
            self.keyversion = 1
        elif FEATURE.REPROG_CONTROLS_V4 in self.device.features:
            self.keyversion = 4
        else:
            if _log.isEnabledFor(_ERROR):
                _log.error(f'Trying to read keys on device {device} which has no REPROG_CONTROLS(_VX) support.')
            self.keyversion = None
        self.keys = [None] * count
        """The mapping from Control IDs to their native Task IDs.
        For example, Control "Left Button" is mapped to Task "Left Click".
        When remapping controls, we point the control we want to remap
        at a target Control ID rather than a target Task ID. This has the
        effect of performing the native task of the target control,
        even if the target itself is also remapped. So remapping
        is not recursive."""
        self.cid_to_tid = {}
        """The mapping from Control ID groups to Controls IDs that belong to it.
        A key k can only be remapped to targets in groups within k.group_mask."""
        self.group_cids = {g: [] for g in special_keys.CID_GROUP}

    def _query_key(self, index: int):
        """Queries the device for a given key and stores it in self.keys."""
        if index < 0 or index >= len(self.keys):
            raise IndexError(index)

        # TODO: add here additional variants for other REPROG_CONTROLS
        if self.keyversion == 1:
            keydata = feature_request(self.device, FEATURE.REPROG_CONTROLS, 0x10, index)
            if keydata:
                cid, tid, flags = _unpack('!HHB', keydata[:5])
                self.keys[index] = ReprogrammableKey(self.device, index, cid, tid, flags)
                self.cid_to_tid[cid] = tid
        elif self.keyversion == 4:
            keydata = feature_request(self.device, FEATURE.REPROG_CONTROLS_V4, 0x10, index)
            if keydata:
                cid, tid, flags1, pos, group, gmask, flags2 = _unpack('!HHBBBBB', keydata[:9])
                flags = flags1 | (flags2 << 8)
                self.keys[index] = ReprogrammableKeyV4(self.device, index, cid, tid, flags, pos, group, gmask)
                self.cid_to_tid[cid] = tid
                if group != 0:  # 0 = does not belong to a group
                    self.group_cids[special_keys.CID_GROUP[group]].append(cid)
        elif _log.isEnabledFor(_WARNING):
            _log.warn(f"Key with index {index} was expected to exist but device doesn't report it.")

    def _ensure_all_keys_queried(self):
        """The retrieval of key information is lazy, but for certain functionality
        we need to know all keys. This function makes sure that's the case."""
        for (i, k) in enumerate(self.keys):
            if k is None:
                self._query_key(i)

    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 0 or index >= len(self.keys):
                raise IndexError(index)

            if self.keys[index] is None:
                self._query_key(index)

            return self.keys[index]

        elif isinstance(index, slice):
            indices = index.indices(len(self.keys))
            return [self.__getitem__(i) for i in range(*indices)]

    def index(self, value):
        for index, k in enumerate(self.keys):
            if k is not None and int(value) == int(k.key):
                return index

        for index, k in enumerate(self.keys):
            if k is None:
                k = self.__getitem__(index)
                if k is not None:
                    return index

    def __iter__(self):
        for k in range(0, len(self.keys)):
            yield self.__getitem__(k)

    def __len__(self):
        return len(self.keys)


#
#
#


def feature_request(device, feature, function=0x00, *params, no_reply=False):
    if device.online and device.features:
        if feature in device.features:
            feature_index = device.features.index(int(feature))
            return device.request((feature_index << 8) + (function & 0xFF), *params, no_reply=no_reply)


def get_firmware(device):
    """Reads a device's firmware info.

    :returns: a list of FirmwareInfo tuples, ordered by firmware layer.
    """
    count = feature_request(device, FEATURE.DEVICE_FW_VERSION)
    if count:
        count = ord(count[:1])

        fw = []
        for index in range(0, count):
            fw_info = feature_request(device, FEATURE.DEVICE_FW_VERSION, 0x10, index)
            if fw_info:
                level = ord(fw_info[:1]) & 0x0F
                if level == 0 or level == 1:
                    name, version_major, version_minor, build = _unpack('!3sBBH', fw_info[1:8])
                    version = '%02X.%02X' % (version_major, version_minor)
                    if build:
                        version += '.B%04X' % build
                    extras = fw_info[9:].rstrip(b'\x00') or None
                    fw_info = _FirmwareInfo(FIRMWARE_KIND[level], name.decode('ascii'), version, extras)
                elif level == FIRMWARE_KIND.Hardware:
                    fw_info = _FirmwareInfo(FIRMWARE_KIND.Hardware, '', str(ord(fw_info[1:2])), None)
                else:
                    fw_info = _FirmwareInfo(FIRMWARE_KIND.Other, '', '', None)

                fw.append(fw_info)
                # if _log.isEnabledFor(_DEBUG):
                #     _log.debug("device %d firmware %s", devnumber, fw_info)
        return tuple(fw)


def get_kind(device):
    """Reads a device's type.

    :see DEVICE_KIND:
    :returns: a string describing the device type, or ``None`` if the device is
    not available or does not support the ``DEVICE_NAME`` feature.
    """
    kind = feature_request(device, FEATURE.DEVICE_NAME, 0x20)
    if kind:
        kind = ord(kind[:1])
        # if _log.isEnabledFor(_DEBUG):
        #     _log.debug("device %d type %d = %s", devnumber, kind, DEVICE_KIND[kind])
        return DEVICE_KIND[kind]


def get_name(device):
    """Reads a device's name.

    :returns: a string with the device name, or ``None`` if the device is not
    available or does not support the ``DEVICE_NAME`` feature.
    """
    name_length = feature_request(device, FEATURE.DEVICE_NAME)
    if name_length:
        name_length = ord(name_length[:1])

        name = b''
        while len(name) < name_length:
            fragment = feature_request(device, FEATURE.DEVICE_NAME, 0x10, len(name))
            if fragment:
                name += fragment[:name_length - len(name)]
            else:
                _log.error('failed to read whole name of %s (expected %d chars)', device, name_length)
                return None

        return name.decode('ascii')


def get_battery(device):
    """Reads a device's battery level."""
    battery = feature_request(device, FEATURE.BATTERY_STATUS)
    if battery:
        discharge, dischargeNext, status = _unpack('!BBB', battery[:3])
        discharge = None if discharge == 0 else discharge
        if _log.isEnabledFor(_DEBUG):
            _log.debug(
                'device %d battery %d%% charged, next level %d%% charge, status %d = %s', device.number, discharge,
                dischargeNext, status, BATTERY_STATUS[status]
            )
        return discharge, BATTERY_STATUS[status], dischargeNext


def get_voltage(device):
    battery_voltage = feature_request(device, FEATURE.BATTERY_VOLTAGE)
    if battery_voltage:
        return decipher_voltage(battery_voltage)


# modified to be much closer to battery reports
def decipher_voltage(voltage_report):
    voltage, flags = _unpack('>HB', voltage_report[:3])
    status = BATTERY_STATUS.discharging
    charge_sts = ERROR.unknown
    charge_lvl = CHARGE_LEVEL.average
    charge_type = CHARGE_TYPE.standard

    if flags & (1 << 7):
        status = BATTERY_STATUS.recharging
        charge_sts = CHARGE_STATUS[flags & 0x03]
    if charge_sts is None:
        charge_sts = ERROR.unknown
    elif charge_sts == CHARGE_STATUS.full:
        charge_lvl = CHARGE_LEVEL.full
        status = BATTERY_STATUS.full
    if (flags & (1 << 3)):
        charge_type = CHARGE_TYPE.fast
    elif (flags & (1 << 4)):
        charge_type = CHARGE_TYPE.slow
        status = BATTERY_STATUS.slow_recharge
    elif (flags & (1 << 5)):
        charge_lvl = CHARGE_LEVEL.critical

    if _log.isEnabledFor(_DEBUG):
        _log.debug(
            'device ???, battery voltage %d mV, charging = %s, charge status %d = %s, charge level %s, charge type %s',
            voltage, status, (flags & 0x03), charge_sts, charge_lvl, charge_type
        )

    return charge_lvl, status, voltage, charge_sts, charge_type


def get_keys(device):
    # TODO: add here additional variants for other REPROG_CONTROLS
    count = None
    if FEATURE.REPROG_CONTROLS in device.features:
        count = feature_request(device, FEATURE.REPROG_CONTROLS)
    elif FEATURE.REPROG_CONTROLS_V4 in device.features:
        count = feature_request(device, FEATURE.REPROG_CONTROLS_V4)
    if count:
        return KeysArray(device, ord(count[:1]))


def get_mouse_pointer_info(device):
    pointer_info = feature_request(device, FEATURE.MOUSE_POINTER)
    if pointer_info:
        dpi, flags = _unpack('!HB', pointer_info[:3])
        acceleration = ('none', 'low', 'med', 'high')[flags & 0x3]
        suggest_os_ballistics = (flags & 0x04) != 0
        suggest_vertical_orientation = (flags & 0x08) != 0
        return {
            'dpi': dpi,
            'acceleration': acceleration,
            'suggest_os_ballistics': suggest_os_ballistics,
            'suggest_vertical_orientation': suggest_vertical_orientation
        }


def get_vertical_scrolling_info(device):
    vertical_scrolling_info = feature_request(device, FEATURE.VERTICAL_SCROLLING)
    if vertical_scrolling_info:
        roller, ratchet, lines = _unpack('!BBB', vertical_scrolling_info[:3])
        roller_type = (
            'reserved', 'standard', 'reserved', '3G', 'micro', 'normal touch pad', 'inverted touch pad', 'reserved'
        )[roller]
        return {'roller': roller_type, 'ratchet': ratchet, 'lines': lines}


def get_hi_res_scrolling_info(device):
    hi_res_scrolling_info = feature_request(device, FEATURE.HI_RES_SCROLLING)
    if hi_res_scrolling_info:
        mode, resolution = _unpack('!BB', hi_res_scrolling_info[:2])
        return mode, resolution


def get_pointer_speed_info(device):
    pointer_speed_info = feature_request(device, FEATURE.POINTER_SPEED)
    if pointer_speed_info:
        pointer_speed_hi, pointer_speed_lo = _unpack('!BB', pointer_speed_info[:2])
        # if pointer_speed_lo > 0:
        #     pointer_speed_lo = pointer_speed_lo
        return pointer_speed_hi + pointer_speed_lo / 256


def get_lowres_wheel_status(device):
    lowres_wheel_status = feature_request(device, FEATURE.LOWRES_WHEEL)
    if lowres_wheel_status:
        wheel_flag = _unpack('!B', lowres_wheel_status[:1])[0]
        wheel_reporting = ('HID', 'HID++')[wheel_flag & 0x01]
        return wheel_reporting


def get_hires_wheel(device):
    caps = feature_request(device, FEATURE.HIRES_WHEEL, 0x00)
    mode = feature_request(device, FEATURE.HIRES_WHEEL, 0x10)
    ratchet = feature_request(device, FEATURE.HIRES_WHEEL, 0x030)

    if caps and mode and ratchet:
        # Parse caps
        multi, flags = _unpack('!BB', caps[:2])

        has_invert = (flags & 0x08) != 0
        has_ratchet = (flags & 0x04) != 0

        # Parse mode
        wheel_mode, reserved = _unpack('!BB', mode[:2])

        target = (wheel_mode & 0x01) != 0
        res = (wheel_mode & 0x02) != 0
        inv = (wheel_mode & 0x04) != 0

        # Parse Ratchet switch
        ratchet_mode, reserved = _unpack('!BB', ratchet[:2])

        ratchet = (ratchet_mode & 0x01) != 0

        return multi, has_invert, has_ratchet, inv, res, target, ratchet


def get_new_fn_inversion(device):
    state = feature_request(device, FEATURE.NEW_FN_INVERSION, 0x00)
    if state:
        inverted, default_inverted = _unpack('!BB', state[:2])
        inverted = (inverted & 0x01) != 0
        default_inverted = (default_inverted & 0x01) != 0
        return inverted, default_inverted


def get_host_names(device):
    state = feature_request(device, FEATURE.HOSTS_INFO, 0x00)
    host_names = {}
    if state:
        capability_flags, _ignore, numHosts, currentHost = _unpack('!BBBB', state[:4])
        if capability_flags & 0x01:  # device can get host names
            for host in range(0, numHosts):
                hostinfo = feature_request(device, FEATURE.HOSTS_INFO, 0x10, host)
                _ignore, status, _ignore, numPages, nameLen, _ignore = _unpack('!BBBBBB', hostinfo[:6])
                name = ''
                remaining = nameLen
                while remaining > 0:
                    name_piece = feature_request(device, FEATURE.HOSTS_INFO, 0x30, host, nameLen - remaining)
                    name += name_piece[2:2 + min(remaining, 14)].decode()
                    remaining = max(0, remaining - 14)
                host_names[host] = (bool(status), name)
    return host_names


def set_host_name(device, name):
    state = feature_request(device, FEATURE.HOSTS_INFO, 0x00)
    if state:
        flags = _unpack('!B', state[:1])[0]
        if flags & 0x02:
            hn = name[:min(14, name.find('.'))] if name.find('.') >= 0 else name
            response = feature_request(device, FEATURE.HOSTS_INFO, 0x40, 0xff, 0, hn)
            return response


def get_polling_rate(device):
    state = feature_request(device, FEATURE.REPORT_RATE, 0x10)
    if state:
        rate = _unpack('!B', state[:1])[0]
        return rate
