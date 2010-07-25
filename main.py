#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import cStringIO

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from data import config
from hardware.tools.hexfile import hexfile
from hardware.tools.patcher import patcher 
from hardware.tools.sysex import sysex

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates')


class MainHandler(webapp.RequestHandler):

  def get_active_firmware(self):
    active_firmware = self.request.get('firmware', None)
    if not active_firmware or active_firmware not in config.firmware_list:
      active_firmware = sorted(config.firmware_list)[0]
    return active_firmware
  
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    template_path = os.path.join(TEMPLATE_PATH, 'index.html')

    active_firmware = self.get_active_firmware()
    active_firmware_data = config.firmware_list[active_firmware]
    p = patcher.Patcher(active_firmware_data[1], active_firmware_data[2])
    
    firmware_list = []
    for name, data in sorted(config.firmware_list.items()):
      description, _, _, _ = data
      firmware_list.append({
          'name': name,
          'description': description,
          'selected': 'selected' if name == active_firmware else ''})
    
    template_data = {
      'title': 'Firmware customization tool',
      'firmware_list': firmware_list,
      'active_firmware': active_firmware_data[0],
      'active_firmware_name': active_firmware,
      'patches': p.GetPatches()
    }
    self.response.out.write(template.render(template_path, template_data))

  def post(self):
    active_firmware = self.get_active_firmware()
    active_firmware_data = config.firmware_list[active_firmware]

    p = patcher.Patcher(active_firmware_data[1], active_firmware_data[2])
    arguments_dict = {}
    for argument in self.request.arguments():
      value = self.request.get(argument)
      if value and argument != 'firmware' and argument != 'format':
        arguments_dict[argument] = value
    if 'wavetable.wavetable_custom' in arguments_dict:
      del arguments_dict['wavetable.wavetable']
    modified_firmware = p.Patch(arguments_dict)
    
    if self.request.get('format') == 'midi':
      sysex_options = sysex.SysExOptions(*active_firmware_data[3])
      data = sysex.CreateSysExMidiFile(modified_firmware, sysex_options)
      mime_type = 'application/x-midi'
      extension = 'mid'
    else:
      f = cStringIO.StringIO()
      hexfile.WriteHexFile(modified_firmware, f, chunk_size=16)
      data = f.getvalue()
      f.close()
      mime_type = 'application/octet-stream'
      extension = 'hex'
    
    self.response.headers['Content-Type'] = mime_type
    self.response.headers['Content-disposition'] = (
        'attachment; filename=%s_custom.%s' % (active_firmware, extension))
    self.response.out.write(data)


def main():
  application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
