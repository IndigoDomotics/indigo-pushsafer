#! /usr/bin/env python
# -*- coding: utf-8 -*-

import httplib, urllib, sys, os

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
			't': self.prepareTextValue(pluginAction.props['msgTitle']),
			'm': self.prepareTextValue(pluginAction.props['msgBody'])
		}

		#populate optional parameters
		if pluginAction.props['msgDevice'] is not None:
			params['d'] = pluginAction.props['msgDevice'].strip()

		if pluginAction.props['msgSound'] is not None:
			params['s'] = pluginAction.props["msgSound"].strip()
			
		if pluginAction.props['msgVibration'] is not None:
			params['v'] = pluginAction.props["msgVibration"].strip()
			
		if pluginAction.props['msgIcon'] is not None:
			params['i'] = pluginAction.props["msgIcon"].strip()			
			
		if pluginAction.props['msgTime2Live'] is not None:
			params['l'] = pluginAction.props["msgTime2Live"].strip()			

		if pluginAction.props['msgSupLinkTitle'] is not None:
			params['ut'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

		if pluginAction.props['msgSupLinkUrl'] is not None:
			params['u'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])

		conn = httplib.HTTPSConnection("pushsafer.com:443")
		conn.request(
			"POST",
			"/api",
			urllib.urlencode(params),
			{"Content-type": "application/x-www-form-urlencoded"}
		)
		conn.close()
