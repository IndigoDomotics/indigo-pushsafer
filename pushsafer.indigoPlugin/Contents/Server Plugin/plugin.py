#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import base64

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = True
        self.fileParameters = ["p", "p2", "p3"]

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
            
        if self.present(pluginAction.props.get('msgSupLinkUrl')):
            params['u'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])
       
        if self.present(pluginAction.props.get('msgSupLinkTitle')):
            params['ut'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

        if self.present(pluginAction.props.get('msgTime2Live')):
            params['l'] = pluginAction.props["msgTime2Live"].strip()            

        if self.present(pluginAction.props.get('msgAttachment')):
            count = 0
            files = self.prepareTextValue(pluginAction.props['msgAttachment'])
            fileList = files.split(",")
            for file in fileList:

                if count == len(self.fileParameters):
                    self.debugLog(u"Warning: too many files specified, skipping the rest...")
                    break

                attachFile = file.strip().lower()

                if os.path.isfile(attachFile) and attachFile.endswith(('.jpg', '.jpeg')):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[self.fileParameters[count]] = "data:image/jpeg;base64," + base64.b64encode(image_file.read())
                            self.debugLog(u"Including as parameter '{}': {}".format(self.fileParameters[count], attachFile))
                    else:
                        self.debugLog(u"Warning: attached file '{}' was too large, attachment was skipped".format(attachFile))
                    
                elif os.path.isfile(attachFile) and attachFile.endswith('.png'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[self.fileParameters[count]] = "data:image/png;base64," + base64.b64encode(image_file.read())
                            self.debugLog(u"Including as parameter '{}': {}".format(self.fileParameters[count], attachFile))
                    else:
                        self.debugLog(u"Warning: attached file '{}' was too large, attachment was skipped".format(attachFile))
                    
                elif os.path.isfile(attachFile) and attachFile.endswith('.gif'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[self.fileParameters[count]] = "data:image/gif;base64," + base64.b64encode(image_file.read())
                            self.debugLog(u"Including as parameter '{}': {}".format(self.fileParameters[count], attachFile))
                    else:
                        self.debugLog(u"Warning: attached file '{}' was too large, attachment was skipped".format(attachFile))
                        
                else:
                    self.debugLog(u"Warning: file '{}' does not exist, or is not a supported file type, attachment was skipped".format(attachFile))
                
                count = count + 1

        r = requests.post("https://www.pushsafer.com/api", data = params)
        self.debugLog(u"Result: {}: {}".format(r.status_code, r.text))
