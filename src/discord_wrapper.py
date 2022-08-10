import requests
import urllib.parse

baseDiscordUrl = 'https://discord.com/api'

# Requests an OAuth2 token from Discord using the user's authorization code.
def getToken(authCode, hostUrl, clientId, clientSecret):
    tokenRequestData = {
        'client_id': clientId,
        'client_secret': clientSecret,
        'grant_type': 'authorization_code',
        'code': authCode,
        'redirect_uri': f'{hostUrl}redirect'
    }
    discordTokenResponse = requests.post('https://discord.com/api/oauth2/token', data=tokenRequestData, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return discordTokenResponse.json()

# Refreshes a Discord OAuth2 token previously obtained from getToken()
def refreshToken(refreshToken, clientId, clientSecret):
    tokenRequestData = {
        'client_id': clientId,
        'client_secret': clientSecret,
        'grant_type': 'refresh_token',
        'refresh_token': refreshToken
    }
    discordTokenResponse = requests.post('https://discord.com/api/oauth2/token', data=tokenRequestData, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return discordTokenResponse.json()

# Constructs a sign-in URL to use in order to obtain the user authorization code.
def getSigninUrl(clientId, redirectUri, scope):
    return f'{baseDiscordUrl}/oauth2/authorize?client_id={clientId}&redirect_uri={urllib.parse.quote(redirectUri, "")}&response_type=code&scope={urllib.parse.quote(scope)}'

# Calls the /users/@me endpoint using the provided access token. Returns the response JSON.
def getUserInfo(accessToken):
    return requests.get(f'{baseDiscordUrl}/users/@me', headers={'Authorization': f'Bearer {accessToken}'}).json()