# 

import os
import pandas as pd
import json as js
import pickle
import hashlib 
import datetime

class Sessions:
    sessions = {}
    
    def __init__(self, Logger=None):
        self.logger = Logger

        savedSessionData = os.path.join('.', 'SessionData.shn')
        if os.path.exists(savedSessionData):
            if self.logger is not None:
                self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Loading saved session data...")
            try: 
                self.sessions = pickle.load(open(savedSessionData, 'rb'))
            except Exception as e:
                if self.logger is not None:
                    self.logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while loading saved session data: {e}")
        else:
            if self.logger is not None:
                self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: No saved session data found. Starting with empty session data.")
            self.sessions = {
                "LoadedSessionIDs": [],
                "VETeamLeads": {}
            }

    def ReadSessionJson(self, inputPath, archivePath):
        files = []
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Reading session JSON files from {inputPath}...")
        for each in os.listdir(inputPath):
            if each.endswith('.json'):
                files.append(os.path.join(inputPath, each))

        for file in files:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Processing file: {file}")   
            sessionData = js.JSONDecoder().decode(open(file).read())
        
            leadCall = sessionData['teamLead']['call']
            sessionDate = sessionData['date']
            sessionID = str(hashlib.sha512((f"{leadCall}-{sessionDate}").encode()).hexdigest())
            
            veList = pd.DataFrame(sessionData['VEs'])
            applicantList = pd.DataFrame(sessionData['applicants'])
            signingVEList = applicantList["signingVes"].dropna()

            if sessionID in self.sessions["LoadedSessionIDs"]:
                self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Duplicate session ID: {sessionID} \n File: {file}")
            else: 
                if self.logger is not None:
                    self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: New session ID: {sessionID}")
                self.sessions["LoadedSessionIDs"].append(sessionID)
                if leadCall not in self.sessions["VETeamLeads"]:
                    veList["SessionCount"] = 1
                    signingVEList["SessionCount"] = 1
                    
                    leadTemplate = {leadCall: {"VEList": veList, "Applicants": applicantList, "SigningVEList":  signingVEList}}
                    self.sessions["VETeamLeads"].update(leadTemplate)
                else:
                    for ve in veList["call"]:
                        if ve not in self.sessions["VETeamLeads"][leadCall]["VEList"]["call"].values:
                            self.sessions["VETeamLeads"][leadCall]["VEList"] = self.sessions["VETeamLeads"][leadCall]["VEList"].append(veList[veList["call"] == ve], ignore_index=True)
                        else:
                            self.sessions["VETeamLeads"][leadCall]["VEList"].loc[self.sessions["VETeamLeads"][leadCall]["VEList"]["call"] == ve, "SessionCount"] += 1
            if self.logger is not None:
                self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Finished processing file: {file}")
            if(not os.path.exists(archivePath)):
                self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Archive path {archivePath} does not exist. Creating it.")
                os.mkdir(archivePath)
            os.rename(file, f"{os.path.join(archivePath, file.split(os.sep)[-1])}")
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Finished reading session JSON files.")
        try:
            self.SaveSessionData("SessionData")
        except Exception as e:
            self.logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while saving session data: {e}")

    def OutputSessionsData(self, teamName, outputPath, outputFile):
        pass
    
    def getVETeams(self):
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Retrieving VETeam names.")
        return list(self.sessions["VETeamLeads"].keys())

    def OutputVEList(self, teamName, outputPath, outputFile):
        veList = self.sessions["VETeamLeads"][teamName]["VEList"]
        veList.sort_values(by="SessionCount", ascending=False) \
            .to_excel(f"{os.path.join(outputPath, outputFile)}.xlsx", index=False)

    def OpenDirectory(self, path):
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Opening directory: {path}")
        try:
            if os.path.exists(path):
                if self.logger is not None:
                    self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Directory exists. Opening...")
                os.startfile(path)
        except Exception as e:
            self.logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while opening directory: {e}")

    def SaveSessionData(self, fileName):
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Saving session data to {fileName}.shn")
        with open(f'{fileName}.shn', 'wb') as file:
            pickle.dump(self.sessions, file, protocol=pickle.HIGHEST_PROTOCOL)
    
    def LoadSessionData(self, fileName):
        if self.logger is not None:
            self.logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Loading session data from {fileName}.shn")
        with open(f'{fileName}.shn', 'rb') as file:
            self.sessions = pickle.load(file)
