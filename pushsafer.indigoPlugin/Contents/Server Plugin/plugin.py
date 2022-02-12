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
        self.logLevel = int(pluginPrefs.get("logLevel", logging.INFO))
        self.indigo_log_handler.setLevel(self.logLevel)
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)
        self.logger.debug(f"logLevel = {self.logLevel}")

    def startup(self):
        self.logger.debug("Pushsafer startup")

    def shutdown(self):
        self.logger.debug("Pushsafer shutdown")

    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            self.logLevel = int(valuesDict.get("logLevel", logging.INFO))
            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(f"New logLevel = {self.logLevel}")

    # helper functions
    @staticmethod
    def present(prop):
        return prop and prop.strip() != ""

    def prepareTextValue(self, strInput):

        if strInput is None:
            return strInput
        else:
            strInput = self.substitute(strInput.strip())

            # fix issue with special characters
            strInput = strInput.encode('utf8')

            self.logger.debug(f"Stripped Text: {strInput}")

            return strInput

    # actions go here
    def sendPushsaver(self, pluginAction, saferDevice, callerWaitingForResult):

        accountKey = saferDevice.pluginProps.get('privatekey', None)
        if not accountKey:
            self.logger.error(f"{saferDevice.name}: Pushsafer account key not configure for device.  Aborting message.")
            return False

        # fill params dictionary with required values
        params = {
            'k': accountKey.strip(),
            'm': self.prepareTextValue(pluginAction.props['msgBody'])
        }

        # populate optional parameters

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

        if self.present(pluginAction.props.get('msgPriority')):
            params['pr'] = pluginAction.props["msgPriority"].strip()

        if self.present(pluginAction.props.get('msgRetry')):
            params['re'] = pluginAction.props["msgRetry"].strip()

        if self.present(pluginAction.props.get('msgExpire')):
            params['ex'] = pluginAction.props["msgExpire"].strip()

        if self.present(pluginAction.props.get('msgAnswer')):
            params['a'] = pluginAction.props["msgAnswer"].strip()

        if self.present(pluginAction.props.get('msgAttachment')):
            count = 0
            fileParameters = ["p", "p2", "p3"]
            files = self.prepareTextValue(pluginAction.props['msgAttachment'])
            fileList = files.split(",")
            for file in fileList:

                if count == len(fileParameters):
                    self.logger.warning(f"{saferDevice.name}: Too many files specified, skipping the rest...")
                    break

                attachFile = file.strip().lower()

                if os.path.isfile(attachFile) and attachFile.endswith(('.jpg', '.jpeg')):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = b"data:image/jpeg;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(f"{saferDevice.name}: Including as parameter '{fileParameters[count]}': {attachFile}")
                    else:
                        self.logger.debug(f"{saferDevice.name}: attached file '{attachFile}' was too large, attachment was skipped")

                elif os.path.isfile(attachFile) and attachFile.endswith('.png'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = b"data:image/png;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(f"{saferDevice.name}: Including as parameter '{fileParameters[count]}': {attachFile}")
                    else:
                        self.logger.debug(f"{saferDevice.name}: attached file '{attachFile}' was too large, attachment was skipped")

                elif os.path.isfile(attachFile) and attachFile.endswith('.gif'):
                    if os.path.getsize(attachFile) <= 2621440:
                        with open(attachFile, "rb") as image_file:
                            params[fileParameters[count]] = b"data:image/gif;base64," + base64.b64encode(image_file.read())
                            self.logger.debug(f"{saferDevice.name}: Including as parameter '{fileParameters[count]}': {attachFile}")
                    else:
                        self.logger.debug(f"{saferDevice.name}: attached file '{attachFile}' was too large, attachment was skipped")

                else:
                    self.logger.warning(
                        f"{saferDevice.name}: file '{attachFile}' does not exist, or is not a supported file type, attachment was skipped")

                count = count + 1

        r = requests.post("https://www.pushsafer.com/api", data=params)
        self.logger.debug(f"POST Result: {r.text}")
        result = json.loads(r.text)

        if result["status"]:
            self.logger.info(f"{saferDevice.name}: Notification sent successfully")
            saferDevice.updateStateOnServer(key="status", value="Success")
            saferDevice.updateStateOnServer(key="message", value=result["success"])
            saferDevice.updateStateOnServer(key="available", value=result["available"])
        else:
            self.logger.warning(f"{saferDevice.name}: Notification failed with error: {result['error']}")
            saferDevice.updateStateOnServer(key="status", value="Error")
            saferDevice.updateStateOnServer(key="message", value=result["error"])
