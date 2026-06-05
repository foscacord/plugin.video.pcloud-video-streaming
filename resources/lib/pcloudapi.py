# coding=utf-8
from xbmc import log, LOGERROR, LOGDEBUG
import requests
import json
from urllib.parse import urlencode
import hashlib
import time

class pCloudAPI :
	def __init__(self):
		self.sess = requests.Session()
		self.apiLocation = 'api.pcloud.com'
		self.TOKEN_EXPIRATION_SECONDS = 1200
		self.auth = None
		self.http_errors = 0
		self.last_error = ''

	def Kill(self):
		self.sess.close()

	def BuildAPIInitialPath(self):
		return 'https://' + self.apiLocation + '/'
	def BuildAPICommandPath(self, command, params, isGet = True):
		if params is not None:
			if isGet:
				return self.BuildAPIInitialPath() + command + '?' + params
			else:
				return self.BuildAPIInitialPath() + command
		else:
			return self.BuildAPIInitialPath() + command
	def GetErrorMessage(self, errorCode):
		return ""	#TODO
	
	def ExecuteRequest(self, apiMethod, paramsUrlEncoded, isGet = True):
		# Build the URL and, then, execute the request
		url = self.BuildAPICommandPath(apiMethod, paramsUrlEncoded, isGet = isGet)
		
		try:
			if isGet:
				response = self.sess.get(url, timeout = 30)
			else:
				if paramsUrlEncoded != None:
					response = self.sess.post(url, timeout = 30, data = paramsUrlEncoded)
				else:
					response = self.sess.post(url, timeout = 30)
			log('plugin.video.pcloud-video-streaming: ' + response.url, LOGDEBUG)
			if response.status_code != 200:
				self.http_errors += 1
				self.last_error = 'HTTP-%d' % response.status_code
				return dict(result=7000, error='HTTP-%d' % response.status_code)
			
			return json.loads(response.text)
		except Exception as e:
			self.http_errors += 1
			self.last_error = str(e)
			log('plugin.video.pcloud-video-streaming: !!! Error calling ' + apiMethod + ': ' + str(e), LOGERROR)
			return dict(result=7000, error=str(e))

	def CheckIfAuthPresent(self, forceReAutenticate = False):
		# Check if auth token is still valid, otherwise re-authenticate
		if self.auth is None:
			self.auth = self.Logon(forceReAutenticate)
		else:
			authAge = time.time() - self.auth["authtime"]
			if forceReAutenticate or (self.TOKEN_EXPIRATION_SECONDS < authAge):
				self.auth = self.Logon(forceReAutenticate)

	# Performs the two-step authentication. Returns an auth token
	def Logon(self, forceReAutenticate=False):
		username = self.addon.getSetting('pcloud_username')
		password = self.addon.getSetting('pcloud_password')
		# If the password has been saved, it has been encrypted and must be decrypted
		if password == 'NO_PASSWORD_SAVED':
			password = ''
		else:
			password = self.EncryptionDecryption(password)
		if self.auth is None or forceReAutenticate is True:
			# Parameters needed by the getdigest API call
			digestParams = urlencode({ "getauth": 1, "logout": 1, "username": username })
			response = self.ExecuteRequest('getdigest', digestParams)
			if response["result"]:
				raise Exception("Error calling getdigest: " + self.GetErrorMessage(response["result"]))
			log('plugin.video.pcloud-video-streaming: getdigest response is: ' + str(response), LOGDEBUG)
			# Response contains digest, necessary for the second step and for token exchange.
			# Compute password's SHA-1
			passwordDigest = hashlib.sha1((password + str.encode(self.addon.getSetting('pcloud_username'))) \
				+ str.encode(response['digest'])).hexdigest()

			# Kodi 21 Omega fix (June 2026): pCloud deprecated the 'userinfo' endpoint
			# for digest-based authentication. The endpoint no longer returns an auth token.
			# Switching to the 'login' endpoint which correctly returns an auth token.
			# Also removed the 'logout=1' parameter which prematurely invalidated sessions.
			authApi = 'login'
			params = { "getauth": 1, "username": username, "digest": response["digest"],
						"authexpire": str(self.TOKEN_EXPIRATION_SECONDS), "passworddigest": passwordDigest }
			paramsUrlEncoded = urlencode(params)
			response = self.ExecuteRequest(authApi, paramsUrlEncoded)
			if response["result"]:
				errorMessage = self.GetErrorMessage(response["result"])
				raise Exception("Error calling login: " + errorMessage)
			self.auth = response["auth"]
			return self.auth

	def ListFolderContents(self, folderNameOrID, isMyShares = False):
		self.CheckIfAuthPresent()
		tryAgain = True
		while (tryAgain):
			tryAgain = False
			# TODO: parametrize or globablise MAXRETRIES
			if isinstance(folderNameOrID, int):
				params = urlencode({ "folderid": folderNameOrID, "auth": self.auth["auth"] })
			else:
				params = urlencode({ "path": folderNameOrID, "auth": self.auth["auth"] })
			if isMyShares:
				#Special functions for shared items
				response = self.ExecuteRequest('listshares', params)
			else:
				response = self.ExecuteRequest('listfolder', params)
			if response["result"] == 0:
				if 'metadata' in response:
					return response["metadata"]["contents"]
				else:
					return []
			elif response["result"] == 1004:   #Token expired mid-session
				self.auth = self.Logon(True)
				tryAgain = True
			else:
				raise Exception("Error calling listfolder: " + self.GetErrorMessage(response["result"]))

	def GetFileLink(self, fileNameOrID, isMyShares = False):
		link = None
		log('plugin.video.pcloud-video-streaming: getting link to {}'.format(fileNameOrID), LOGDEBUG)
		self.CheckIfAuthPresent()
		for retry in range(2):
			if isinstance(fileNameOrID, int):
				params = urlencode({ "fileid": fileNameOrID, "auth": self.auth["auth"], "skipfilename": "1" })
			else:
				params = urlencode({ "path": fileNameOrID, "auth": self.auth["auth"], "skipfilename": "1" })
			response = self.ExecuteRequest('getfilelink', params)
			if response["result"] == 0:
				try:
					link = "https://" + response["hosts"][0] + response["path"]
				except:
					raise Exception("Malformed response from getfilelink")
			elif response["result"] == 1004:
				raise Exception("Token expired — can't retry")
				self.auth = self.Logon(True)
				continue
			elif response["result"] == 7000 or response["result"] == 5000:
				if retry == 0:
					continue
			else:
				raise Exception("Error calling getfilelink: " + self.GetErrorMessage(response["result"]))
			break
		return link

	def GetThumbnailLinks(self, folderOrFileID, isMyShares = False):
		links = []
		log('plugin.video.pcloud-video-streaming: getting thumbnail links', LOGDEBUG)
		self.CheckIfAuthPresent()
		if isinstance(folderOrFileID, int):
			params = urlencode({ "fileid": folderOrFileID, "auth": self.auth["auth"] })
		else:
			params = urlencode({ "path": folderOrFileID, "auth": self.auth["auth"] })
		response = self.ExecuteRequest('getthumbslinks', params)
		if response["result"] == 0:
			for thumb in response["thumbslinks"]["thumbs"]:
				links.append("https://" + thumb["hosts"][0] + thumb["path"])
		elif response["result"] == 1004:
			raise Exception("Token expired — can't retry")
			self.auth = self.Logon(True)
		else:
			raise Exception("Error calling getthumbslinks: " + self.GetErrorMessage(response["result"]))
		return links

	def EncryptionDecryption(self, input):
		key = self.addon.getSetting('') #Empty uuid
		key = ''.join(chr(ord(c) % 16 + 48) for c in key) if key else '0000' #Fallback
		key = hashlib.sha256(key.encode()).hexdigest()[:48]
		return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(input, key))
