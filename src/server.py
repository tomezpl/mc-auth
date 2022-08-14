from datetime import datetime, timedelta
from os import getcwd
import os.path
from time import time
from flask import Flask, request, make_response, redirect, Response
from werkzeug.exceptions import BadRequest, Unauthorized
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

def writeFile(filePath, fileContents, newFile=False):
    file = open(filePath, 'x' if newFile else 'w')
    file.write(fileContents)
    file.close()

appsettings = json.loads(readFile('appsettings.json'))

# A dict that will store people's Minecraft player names where the key is their Discord ID snowflake.
minecraftNameMap = {}

# Loads the Minecraft player name map from the JSON file or creates one if needed.
def loadMinecraftNameMap():
    global minecraftNameMap
    mcNameMapPath = './mc_name_map.json'
    if os.path.exists(mcNameMapPath):
        minecraftNameMap = json.loads(readFile(mcNameMapPath))
    else:
        writeFile(mcNameMapPath, json.dumps({}), True)
        minecraftNameMap = {}

def syncMinecraftNameMap():
    global minecraftNameMap
    mcNameMapPath = './mc_name_map.json'
    writeFile(mcNameMapPath, json.dumps(minecraftNameMap), not os.path.exists(mcNameMapPath))

loadMinecraftNameMap()

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

def getConfigForDiscordId(discordId):
    if discordId in minecraftNameMap:
        return {'minecraftPlayerName': minecraftNameMap[discordId]}
    else:
        return {}

def updateConfigForDiscordId(discordId, mcPlayerName):
    minecraftNameMap[discordId] = mcPlayerName
    syncMinecraftNameMap()

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

@app.route('/gameconfig', methods=['GET'])
def getUserMcConfig():
    sessionUuid = getUuidForSession(request)
    discordToken = getTokenForUuid(sessionUuid)
    print(minecraftNameMap)
    if discordToken:
        userInfo = discord_wrapper.getUserInfo(discordToken['access_token'])
        if userInfo and 'id' in userInfo:
            return getConfigForDiscordId(userInfo['id'])
        else:
            return BadRequest('Could not get Discord user data.')
    else:
        return Unauthorized('Invalid or missing Discord OAuth2 access token.')

@app.route('/gameconfig', methods=['PUT'])
def updateUserMcConfig():
    print('helllooooooo')
    discordId = None
    discordToken = getTokenForUuid(getUuidForSession(request))
    print('helllooooooo2')
    if discordToken and 'access_token' in discordToken:
        userInfo = discord_wrapper.getUserInfo(discordToken['access_token'])
        if userInfo and 'id' in userInfo:
            discordId = userInfo['id']
        else:
            return BadRequest('Could not get Discord user data.')
    else:
        return Unauthorized('Invalid or missing Discord OAuth2 access token.')
    print('helllooooooo3')

    newConfig = request.get_json()
    print(newConfig)
    if newConfig and 'minecraftPlayerName' in newConfig:
        wasJustCreated = not discordId in minecraftNameMap
        print(f'wasJustCreated: {wasJustCreated}')
        minecraftNameMap[discordId] = newConfig['minecraftPlayerName']
        print(f'Updated name map for DiscordUser {discordId} to allow player {newConfig["minecraftPlayerName"]}')
        syncMinecraftNameMap()
        print('Written to file')
        return Response(status=201 if wasJustCreated else 200)
    else:
        return BadRequest('Invalid game configuration update data.')

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