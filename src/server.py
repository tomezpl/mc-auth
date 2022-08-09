from datetime import datetime, timedelta
from os import getcwd
import os.path
from time import time
from flask import Flask, request, make_response, redirect
from werkzeug.exceptions import BadRequest
import requests
import urllib.parse
import json
from uuid import uuid4
import copy

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

def getDiscordToken(authCode, hostUrl):
    tokenRequestData = {
        'client_id': appsettings['discord']['clientId'],
        'client_secret': appsettings['discord']['clientSecret'],
        'grant_type': 'authorization_code',
        'code': authCode,
        'redirect_uri': f'{hostUrl}redirect'
    }
    discordTokenResponse = requests.post('https://discord.com/api/oauth2/token', data=tokenRequestData, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return discordTokenResponse.json()

def refreshDiscordToken(refreshToken):
    tokenRequestData = {
        'client_id': appsettings['discord']['clientId'],
        'client_secret': appsettings['discord']['clientSecret'],
        'grant_type': 'refresh_token',
        'refresh_token': refreshToken
    }
    discordTokenResponse = requests.post('https://discord.com/api/oauth2/token', data=tokenRequestData, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return discordTokenResponse.json()

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
            refreshedToken = refreshDiscordToken(token['refresh_token'])
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
        token = getDiscordToken(request.args['code'], request.host_url)
        response = make_response(token)
        sessionUuid = getUuidForSession(request)
        userTokens[sessionUuid] = copy.copy(token)
        userTokens[sessionUuid]['created'] = datetime.utcnow()
        response.set_cookie('WhitelisterUuid', sessionUuid)
        return response
    else:
        return BadRequest()

@app.route('/signin')
def signin():
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={appsettings["discord"]["clientId"]}&redirect_uri={urllib.parse.quote(appsettings["discord"]["redirectUri"], "")}&response_type=code&scope={urllib.parse.quote(appsettings["discord"]["scope"])}')