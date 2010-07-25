#!/usr/bin/python2.5
#
# Copyright 2010 Olivier Gillet.
#
# Author: Olivier Gillet (ol.gillet@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""HEX file patcher."""

import logging
import sys

sys.path.append('.')

from hardware.tools.hexfile import hexfile
from hardware.tools.sysex import sysex

class Patcher(object):
  
  def __init__(self, definitions_module, firmware_file):
    self._firmware = ''.join(map(chr, hexfile.LoadHexFile(file(firmware_file))))
    assert self._firmware
    patches = __import__(definitions_module, globals(), locals(), ['patches'])
    self._patches = patches.patches
    
  def GetPatches(self):
    categories = {}
    for name, (definition, _) in sorted(self._patches.items()):
      category, name = tuple(name.split('.'))
      description, value_type, value_range, value_default = definition
      categories.setdefault(category, []).append({
          'name': name,
          'description': description,
          'is_upload': value_type == file,
          'value_list': value_range if value_type == list else [],
          'value_range': '%d-%d' % value_range if value_type == int else '',
          'value_length': value_range * 2 if value_type == str else 6,
          'value_default': value_default
          })
    categories_list = []
    for name, content in sorted(categories.items()):
      categories_list.append({
          'name': name,
          'content': content
      })
    return categories_list

  def FixValue(self, value, definition):
    _, value_type, value_range, _ = definition
    if value_type == int:
      try:
        value = int(value)
      except Exception:
        value = 0
      return max(min(value, value_range[1]), value_range[0])
    elif value_type == list:
      return value
    elif value_type == str:
      value = eval('\'' + value.replace('\'', '\\\'') + '\'')[:value_range]
      padding = value_range - len(value)
      return value + ' ' * padding
    else:
      value = value[:value_range]
      padding = value_range - len(value)
      return value + ' ' * padding

  def CheckPatchConsistency(self, patch_point, value):
    to_search, offset, size, modifier = patch_point
    position = self._firmware.find(to_search)
    if position == -1:
      return None
    start = position + offset
    if start < 0 or start >= len(self._firmware):
      return None
    value = modifier(value)
    if len(value) != size or start + size > len(self._firmware):
      return None
    return (start, size, value)
    
  def Patch(self, patches):
    patched_firmware = map(ord, self._firmware)
    for k, v in patches.items():
      if not k in self._patches:
        logging.warning('Ignoring unknown patch: %s' % k)
        continue
      definition, patch_points = self._patches[k]
      value = self.FixValue(v, definition)
      patches = []
      for patch_point in patch_points:
        patch = self.CheckPatchConsistency(patch_point, value)
        if patch is None:
          patches = None
          break
        else:
          patches.append(patch)
      if not patches:
        logging.warning('Cannot apply patch: %s' % k)
        continue
      for start, size, value in patches:
        patched_firmware[start:start + size] = map(ord, value)
    assert len(patched_firmware) == len(self._firmware)
    return patched_firmware
