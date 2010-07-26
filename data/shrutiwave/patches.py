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

"""Patchable blocks of code in the Shruti-1 firmware."""

import os

WAVETABLE_PATH = os.path.join(os.path.split(__file__)[0], 'wavetables')

wavetable_files = sorted(os.listdir(WAVETABLE_PATH))


def FixWavetable(data):
  return ''.join(data[i:i + 128] + data[i] for i in xrange(0, 2048, 128))


patches = {
  'display.brightness': (
      ('LCD brightness', int, (3, 29), 29),
      [('\x8d\xe9\x0e\x94', 0, 2,
        lambda x: '%c%c' % (0x80 + (x % 16), 0xe8 + x / 16))]),
  
  'display.pause_duration': (
      ('Parameter name display delay (ms)', int, (100, 4000), 900),
      [('\x65\x58\x73\x40', 0, 4,
        lambda x: '%c%c%c\x40' % (
            0x60 + (x % 16),
            0x50 + ((x % 256) / 16),
            0x70 + ((x / 256) % 16))),
       ('\x25\x58\x33\x40', 0, 4, 
        lambda x: '%c%c%c\x40' % (
            0x20 + (x % 16),
            0x50 + ((x % 256) / 16),
            0x30 + ((x / 256) % 16)))]),

  'display.splash_screen_line_1': (
      ('Splash screen line 1', str, 16, '\\x06\\x07wave   mutable'),
      [('\x06\x07wave', 0, 16, lambda x: x)]),

  'display.splash_screen_line_2': (
      ('Splash screen line 2', str, 16, 'v0.1 instruments'),
      [('v0.1 instruments', 0, 16, lambda x: x)]),

  'display.first_page_index': (
      ('Index of the page shown at startup', int, (1, 12), 4),
      [('\x83\xe0\x80\x93', 0, 1, lambda x: chr(x - 1 + 0x80))]),
  
  'init.patch_name': (
      ('Default patch name', str, 8, 'new      '),
      [('new     ', 0, 8, lambda x: x)]),
      
  'init.oscillator_1_waveform': (
      ('Default oscillator 1 waveform', int, (0, 5), 0),
      [('new     ', -86, 1, lambda x: chr(x))]),
      
  'init.oscillator_2_waveform': (
      ('Default oscillator 2 waveform', int, (0, 5), 0),
      [('new     ', -86 + 1, 1, lambda x: chr(x))]),

  'init.oscillator_2_range': (
      ('Default oscillator 2 range', int, (-24, 24), -12),
      [('new     ', -86 + 5, 1, lambda x: chr(x) if x >= 0 else chr(256 + x))]),

  'init.oscillator_2_detune': (
      ('Default oscillator 2 detune', int, (0, 127), 16),
      [('new     ', -86 + 7, 1, lambda x: chr(x))]),

  'init.mix': (
      ('Default mix balance', int, (0, 63), 32),
      [('new     ', -86 + 8, 1, lambda x: chr(x))]),

  'init.filter_cutoff': (
      ('Default filter cutoff', int, (0, 127), 100),
      [('new     ', -86 + 12, 1, lambda x: chr(x))]),

  'init.filter_resonance': (
      ('Default filter resonance', int, (0, 63), 0),
      [('new     ', -86 + 13, 1, lambda x: chr(x))]),

  'init.filter_env_amount': (
      ('Default filter envelope modulation', int, (0, 63), 20),
      [('new     ', -86 + 14, 1, lambda x: chr(x))]),

  'init.env1_attack': (
      ('Default envelope 1 attack', int, (0, 127), 0),
      [('new     ', -86 + 16, 1, lambda x: chr(x))]),

  'init.env1_decay': (
      ('Default envelope 1 decay', int, (0, 127), 60),
      [('new     ', -86 + 18, 1, lambda x: chr(x))]),

  'init.env1_level_sustain': (
      ('Default envelope 1 sustain', int, (0, 127), 20),
      [('new     ', -86 + 20, 1, lambda x: chr(x))]),

  'init.env1_release': (
      ('Default envelope 1 release', int, (0, 127), 60),
      [('new     ', -86 + 22, 1, lambda x: chr(x))]),

  'init.env2_attack': (
      ('Default envelope 2 attack', int, (0, 127), 0),
      [('new     ', -86 + 17, 1, lambda x: chr(x))]),

  'init.env2_decay': (
      ('Default envelope 2 decay', int, (0, 127), 40),
      [('new     ', -86 + 19, 1, lambda x: chr(x))]),

  'init.env2_level_sustain': (
      ('Default envelope 2 sustain', int, (0, 127), 80),
      [('new     ', -86 + 21, 1, lambda x: chr(x))]),

  'init.env2_release': (
      ('Default envelope 2 release', int, (0, 127), 40),
      [('new     ', -86 + 23, 1, lambda x: chr(x))]),

  'wavetable.wavetable_1': (
      ('Preset wavetable 1 data file', list, wavetable_files, 'waves.bin'),
      [('\x18\x19\x1b\x1c\x1d\x1f', 0, 2064,
       lambda x: FixWavetable(file(os.path.join(WAVETABLE_PATH, x)).read()))]),
      
  'wavetable.wavetable_1_custom': (
      ('OR: Custom wavetable 1 data file', file, 2048, None),
      [('\x18\x19\x1b\x1c\x1d\x1f', 0, 2064,
       lambda x: FixWavetable(x))]),

  'wavetable.wavetable_2': (
      ('Preset wavetable 2 data file', list, wavetable_files, 'digital.bin'),
      [('\x7d\x83\x8a\x91\x98\xa0', 0, 2064,
       lambda x: FixWavetable(file(os.path.join(WAVETABLE_PATH, x)).read()))]),

  'wavetable.wavetable_2_custom': (
      ('OR: Custom wavetable 2 data file', file, 2048, None),
      [('\x7d\x83\x8a\x91\x98\xa0', 0, 2064,
       lambda x: FixWavetable(x))]),

  'wavetable.wavetable_3': (
      ('Preset wavetable 3 data file', list, wavetable_files, 'bowed.bin'),
      [('\x7a\x85\x91\x9c', 0, 2064,
       lambda x: FixWavetable(file(os.path.join(WAVETABLE_PATH, x)).read()))]),
    
  'wavetable.wavetable_3_custom': (
      ('OR: Custom wavetable 3 data file', file, 2048, None),
      [('\x7a\x85\x91\x9c', 0, 2064,
       lambda x: FixWavetable(x))]),

  'wavetable.wavetable_4': (
      ('Preset wavetable 4 data file', list, wavetable_files, 'metallic.bin'),
      [('\x84\x73\x65\x5d', 0, 2064,
       lambda x: FixWavetable(file(os.path.join(WAVETABLE_PATH, x)).read()))]),
  
  'wavetable.wavetable_4_custom': (
      ('OR: Custom wavetable 4 data file', file, 2048, None),
      [('\x84\x73\x65\x5d', 0, 2064,
       lambda x: FixWavetable(x))]),

  'wavetable.wavetable_5': (
      ('Preset wavetable 5 data file', list, wavetable_files, 'male.bin'),
      [('\x90\x9c\xa5\xae', 0, 2064,
       lambda x: FixWavetable(file(os.path.join(WAVETABLE_PATH, x)).read()))]),

  'wavetable.wavetable_5_custom': (
      ('OR: Custom wavetable 5 data file', file, 2048, None),
      [('\x90\x9c\xa5\xae', 0, 2064,
       lambda x: FixWavetable(x))]),
    
}
