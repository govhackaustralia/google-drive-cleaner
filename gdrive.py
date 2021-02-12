#!/usr/bin/env python3

import requests
import json
import pandas
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.googleapis.com/drive/v3/files/"
fileList = "?pageSize=1000&pageToken="
filePermissions = "/permissions?fields=*"
filePermissionDelete = "/permissions/"
nextPageToken = ''
nextPage = True
fileCount = 0
pageCount = 0


s = requests.Session()
s.verify = False

# IMPORTANT
# An Oauth 2.0 Access Token is required to use this script
# Using a google account with appropriate rights, generate a Client ID and Secret
# instructions = 'https://developers.google.com/drive/api/v3/about-auth?authuser=2'
# authUrl = 'https://accounts.google.com/o/oauth2/auth'
# tokenUrl = 'https://accounts.google.com/o/oauth2/token'
# scope = 'https://www.googleapis.com/auth/drive'

token = "YOUR OATH TOKEN GOES HERE"

s.headers.update({'Authorization': 'Bearer ' + token})


while nextPage:
    pageCount += 1
    requestList = s.get(url + fileList + nextPageToken)
    if requestList.status_code == 401:
        nextPage = False
    if requestList.status_code == 200:
        responseList = requestList.json()

        print(pageCount, " Token: ", nextPageToken)
        if "nextPageToken" in responseList:
            nextPageToken = responseList['nextPageToken']
        else:
            nextPage = False

        for file in responseList['files']:
            fileCount += 1
            requestPermissions = s.get(url + file['id'] + filePermissions)
            if requestPermissions.status_code == 401:
                nextPage = False
            if requestPermissions.status_code == 200:
                responsePermissions = requestPermissions.json()
                for permission in responsePermissions['permissions']:
                    if permission['id'] == 'anyoneWithLink':
                        delete = True
                    
                    elif "emailAddress" in permission:
                        if permission['emailAddress'] == 'partnerandprosper@gmail.com':
                            delete = False
                        elif len(permission['emailAddress'].split("@")) < 2:
                            delete = False
                        elif permission['emailAddress'].split("@")[1] == 'govhack.org':
                            delete = False
                        elif permission['emailAddress'].split("@")[1] == 'govhack.org.nz':
                            delete = False
                        elif permission['emailAddress'].split("@")[1] == 'govhackaotearoa.nz':
                            delete = False
                        else:
                            delete = True
                        
                        if permission['role'] == "owner" and delete == True :
                            delete = False
                            print(fileCount, "Owner Needs changing - ", permission['emailAddress'], " from file ", file['id'], " - ", file['name'] )
                            
                    if delete == True:
                        deletePermissions = s.delete(url + file['id'] + filePermissionDelete + permission['id'])
                        if deletePermissions.status_code == 204:
                            if "emailAddress" in permission:
                                print(fileCount, "Deleting ", permission['emailAddress'], " from file ", file['name'] )
                            elif "id" in permission:
                                print(fileCount, "Deleting ", permission['id'], " from file ", file['name'] )
                        else:
                            print(fileCount, " - User: ", permission['id'], " - File: ", file['id'], " - ", file['name'], " deletePermissions status code: ", deletePermissions.status_code)


            else:
                print(fileCount, "requestPermissions status code: ", requestPermissions.status_code)
            


    else:
        print(fileCount, "requestList status code: ", requestList.status_code)
