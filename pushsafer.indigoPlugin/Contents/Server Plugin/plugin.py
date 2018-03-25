#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import base64
import logging
import json

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = True

        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)

        try:
            self.logLevel = int(self.pluginPrefs[u"logLevel"])
        except:
            self.logLevel = logging.INFO
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u"New logLevel = {}".format(self.logLevel))

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        self.logger.debug(u"Pushsafer startup")

    def shutdown(self):
        self.logger.debug(u"Pushsafer shutdown")

    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            try:
                self.logLevel = int(valuesDict[u"logLevel"])
            except:
                self.logLevel = logging.INFO
            self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u"New logLevel = {}".format(self.logLevel))


    # helper functions
    def present(self, prop):
        return (prop and prop.strip() != "")

    def prepareTextValue(self, strInput):

        if strInput is None:
            return strInput
        else:
            strInput = strInput.strip()

            strInput = self.substitute(strInput)

            #fix issue with special characters
            strInput = strInput.encode('utf8')

            self.logger.debug("Stripped Text: {}".format(strInput))

            return strInput


    # actions go here
    def sendPushsaver(self, pluginAction, saferDevice, callerWaitingForResult):

        accountKey = saferDevice.pluginProps.get('privatekey', None)
        if not accountKey:
            self.logger.error(u"{}: Pushsafer account key not configure for device.  Aborting message.".format(saferDevice.name))
            return False
        
        #fill params dictionary with required values
        params = {
            'k': accountKey.strip(),
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
            fileParameters = ["p", "p2", "p3"]
            files = self.prepareTextValue(pluginAction.props['msgAttachment'])
            fileList = files.split(",")
            for file in fileList:

                if count == len(fileParameters):
                    self.logger.warning(u"{}: Too many files specified, skipping the rest...".format(saferDevice.name))
                    break

                attachFile = file.strip().lower()

                if os.path.isfile(attachFile) and attachFile.endswith(('.jpg', '.jpeg')):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = "data:image/jpeg;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(u"{}: Including as parameter '{}': {}".format(saferDevice.name, fileParameters[count], attachFile))
                    else:
                        self.logger.debug(u"{}: attached file '{}' was too large, attachment was skipped".format(saferDevice.name, attachFile))
                    
                elif os.path.isfile(attachFile) and attachFile.endswith('.png'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = "data:image/png;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(u"{}: Including as parameter '{}': {}".format(saferDevice.name, fileParameters[count], attachFile))
                    else:
                        self.logger.debug(u"{}: attached file '{}' was too large, attachment was skipped".format(saferDevice.name, attachFile))
                    
                elif os.path.isfile(attachFile) and attachFile.endswith('.gif'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = "data:image/gif;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(u"{}: Including as parameter '{}': {}".format(saferDevice.name, fileParameters[count], attachFile))
                    else:
                        self.logger.debug(u"{}: attached file '{}' was too large, attachment was skipped".format(saferDevice.name, attachFile))
                        
                else:
                    self.logger.warning(u"{}: file '{}' does not exist, or is not a supported file type, attachment was skipped".format(saferDevice.name, attachFile))
                
                count = count + 1

        r = requests.post("https://www.pushsafer.com/api", data = params)
        self.logger.debug(u"Result: {}".format(r.text))
        result = json.loads(r.text)
        
        if result["status"]:
            self.logger.info(u"{}: Notification sent successfully".format(saferDevice.name))   
            saferDevice.updateStateOnServer(key="status", value="Success")
            saferDevice.updateStateOnServer(key="message", value=result["success"])
            saferDevice.updateStateOnServer(key="available", value=result["available"])
        else: 
            self.logger.warning(u"{}: Notification failed with error: {}".format(saferDevice.name, result["error"]))   
            saferDevice.updateStateOnServer(key="status", value="Error")
            saferDevice.updateStateOnServer(key="message", value=result["error"])
        