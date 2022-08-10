from datetime import datetime, timedelta
from os import getcwd
import os.path
from time import time
from flask import Flask, request, make_response, redirect
from werkzeug.exceptions import BadRequest
import json
from uuid import uuid4
import copy
import discord_wrapper

app = Flask(__name__)

wwwroot = os.path.join(getcwd(), 'wwwroot')

# Cache the users' Discord Access Tokens in a dict where each key is the UUID generated for their session.
userTokens = {}

def readFile(filePath):
    file = open(filePath)
    fileContents = ''.join(file.readlines())
    file.close()
    return fileContents

appsettings = json.loads(readFile('appsettings.json'))

# Returns a string read from the specified file inside wwwroot.
def wwwrootRead(fileName):
    return readFile(os.path.join(wwwroot, fileName))

def getUuidForSession(currentRequest):
    if 'WhitelisterUuid' in currentRequest.cookies and currentRequest.cookies['WhitelisterUuid']:
        return currentRequest.cookies['WhitelisterUuid']
    else:
        return str(uuid4())

def getTokenForUuid(sessionUuid):
    if sessionUuid in userTokens:
        token = copy.copy(userTokens[sessionUuid])
        expiryDate = token['created'] + timedelta(seconds=float(token['expires_in'])) 
        if expiryDate <= datetime.utcnow() - timedelta(seconds=60):
            if expiryDate <= datetime.utcnow() - timedelta(seconds=15):
                return None
            refreshedToken = discord_wrapper.refreshToken(token['refresh_token'], appsettings['discord']['clientId'], appsettings['discord']['clientSecret'])
            if refreshedToken:
                refreshedToken['created'] = datetime.utcnow()
                userTokens[sessionUuid] = copy.copy(refreshedToken)
                return userTokens[sessionUuid]
        return userTokens[sessionUuid] 
    else:
        return None

@app.route('/mytoken')
def myToken():
    sessionToken = getTokenForUuid(request.cookies['WhitelisterUuid'])
    if sessionToken:
        return sessionToken
    else:
        return {}

@app.route('/userinfo')
def getUserInfo():
    sessionId = getUuidForSession(request)
    userToken = getTokenForUuid(sessionId)
    if userToken:
        discordUserInfo = discord_wrapper.getUserInfo(userToken['access_token'])
        print(discordUserInfo)
        return {'userName': f'{discordUserInfo["username"]}#{discordUserInfo["discriminator"]}'}
    else:
        return {}

@app.route('/')
def home():
    return wwwrootRead('index.html')

@app.route('/main.js')
def js():
    return wwwrootRead('main.js')

@app.route('/redirect')
def signinRedirect():
    # Check that the request contains a valid OAuth2 code.
    if 'code' in request.args and request.args['code']:
        token = discord_wrapper.getToken(request.args['code'], request.host_url, appsettings['discord']['clientId'], appsettings['discord']['clientSecret'])
        response = redirect('/')
        sessionUuid = getUuidForSession(request)
        userTokens[sessionUuid] = copy.copy(token)
        userTokens[sessionUuid]['created'] = datetime.utcnow()
        response.set_cookie('WhitelisterUuid', sessionUuid)
        return response
    else:
        return BadRequest()

@app.route('/signin')
def signin():
    return redirect(discord_wrapper.getSigninUrl(appsettings['discord']['clientId'], appsettings['discord']['redirectUri'], appsettings['discord']['scope']))