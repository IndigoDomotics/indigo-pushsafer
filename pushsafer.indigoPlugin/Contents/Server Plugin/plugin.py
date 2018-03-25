#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, httplib, urllib
import requests

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = True

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        self.debugLog(u"startup called")

    def shutdown(self):
        self.debugLog(u"shutdown called")

    # helper functions
    def present(self, prop):
        return (prop and prop.strip() != "")

    def prepareTextValue(self, strInput):

        if strInput is None:
            return strInput
        else:
            strInput = strInput.strip()

            strInput = self.substitute(strInput)

            self.debugLog(strInput)

            #fix issue with special characters
            strInput = strInput.encode('utf8')

            return strInput

    # actions go here
    def send(self, pluginAction):

        #fill params dictionary with required values
        params = {
            'k': self.pluginPrefs['privatekey'].strip(),
            'm': self.prepareTextValue(pluginAction.props['msgBody'])
        }

        #populate optional parameters
        
        if self.present(pluginAction.props.get('msgTitle')):
            params['t'] = self.prepareTextValue(pluginAction.props['msgTitle'])

        if self.present(pluginAction.props.get('msgDevice')):
            params['d'] = pluginAction.props['msgDevice'].strip()

        if self.present(pluginAction.props.get('msgSound')):
            params['s'] = pluginAction.props["msgSound"].strip()
            
        if self.present(pluginAction.props.get('msgVibration')):
            params['v'] = pluginAction.props["msgVibration"].strip()
            
        if self.present(pluginAction.props.get('msgIcon')):
            params['i'] = pluginAction.props["msgIcon"].strip()         
            
        if self.present(pluginAction.props.get('msgTime2Live')):
            params['l'] = pluginAction.props["msgTime2Live"].strip()            

        if self.present(pluginAction.props.get('msgSupLinkTitle')):
            params['ut'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

        if self.present(pluginAction.props.get('msgSupLinkUrl')):
            params['u'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])

        self.debugLog(u"Params: {}".format(params))

#        conn = httplib.HTTPSConnection("pushsafer.com:443")
#        conn.request(
#           "POST",
#           "/api",
#           "/data/push-send.php",
#           urllib.urlencode(params),
#           {"Content-type": "application/x-www-form-urlencoded"}
#        )
#        r = conn.getresponse().read()
#        conn.close()
#        self.debugLog(u"Result: {}".format(r))
       
        r = requests.post("https://pushsafer.com/api", data = params)
        self.debugLog(u"Result: {}: {}".format(r.status_code, r.text))
