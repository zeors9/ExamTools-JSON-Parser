import logging
import os
import tkinter as tk
from tkinter import ttk
import datetime
from venv import logger
import SessionDataRead
import configparser


class main:
    ImportDirectory = ""
    OutputDirectory = ""
    ArchiveDirectory = ""
    root = tk.Tk()


    def __init__(self):
        config = configparser.ConfigParser()
        if not os.path.exists('settings.ini'):
            config['DEFAULT'] = {
                'ImportDirectory': 'Input',
                'ArchiveDirectory': 'Archive',
                'OutputDirectory': 'Output',
                'LogLevel': 'WARNING'
            }
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)
        else:
            config.read('settings.ini')

        self.setDirectories(config['DEFAULT']['ImportDirectory'], config['DEFAULT']['OutputDirectory'], config['DEFAULT']['ArchiveDirectory'])
            
        logLevel = config['DEFAULT']['LogLevel'].upper()

        logger = logging.getLogger(__name__)
        logging.basicConfig(filename='ExamToolsJSONParser.log')
        if logLevel == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        elif logLevel == 'INFO':
            logging.basicConfig(level=logging.INFO)
        elif logLevel == 'WARNING':
            logging.basicConfig(level=logging.WARNING)
        elif logLevel == 'ERROR':
            logging.basicConfig(level=logging.ERROR)
        elif logLevel == 'CRITICAL':
            logging.basicConfig(level=logging.CRITICAL)
        logger.info(f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}: App Started')

        self.sessions = SessionDataRead.Sessions(logger)
        try:
            logger.info(f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}: Reading session JSON from {self.ImportDirectory} and archiving to {self.ArchiveDirectory}')
            self.sessions.ReadSessionJson(self.ImportDirectory, self.ArchiveDirectory)
        except Exception as e:
            logger.error(f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}: Error occurred while reading session JSON: {e}')

        try:
            self.root.title("Exam Tools Stats Extractor")
            self.root.geometry("500x200")
            self.root.resizable(False, False)
            self.root.scrollbar = tk.Scrollbar(self.root)

            leftPanel = tk.LabelFrame(self.root, text="Settings", width=250, padx=5, pady=10)
            leftPanel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)    

            leftPanelRow1 = tk.Frame(leftPanel)
            leftPanelRow1.pack(fill=tk.X, pady=5)

            leftPanelRow2 = tk.Frame(leftPanel)
            leftPanelRow2.pack(fill=tk.X, pady=5)

            leftPanelRow3 = tk.Frame(leftPanel)
            leftPanelRow3.pack(fill=tk.X, pady=5) 

            tk.Button(leftPanel, text="Open Working Directory", command=lambda: self.OpenDirectory('.')).pack(side=tk.TOP, padx=5)

            tk.Button(leftPanelRow1, text="Open Import Directory", command=lambda: self.OpenDirectory(self.ImportDirectory)).pack(side=tk.LEFT, padx=5)
            importDirEntry = tk.Entry(leftPanelRow1, width=25)
            importDirEntry.insert(0, self.ImportDirectory)
            importDirEntry.pack(side=tk.LEFT, pady=5)

            tk.Button(leftPanelRow2, text="Open Output Directory", command=lambda: self.OpenDirectory(self.OutputDirectory)).pack(side=tk.LEFT, padx=5)
            outputDirEntry = tk.Entry(leftPanelRow2, width=25)
            outputDirEntry.insert(0, self.OutputDirectory)
            outputDirEntry.pack(side=tk.LEFT, pady=5)

            tk.Button(leftPanelRow3, text="Open Archive Directory", command=lambda: self.OpenDirectory(self.ArchiveDirectory)).pack(side=tk.LEFT, padx=5)
            #tk.Label(leftPanelRow3, text="Archive Directory:", width=15).pack(side=tk.LEFT)
            archiveDirEntry = tk.Entry(leftPanelRow3, width=25)
            archiveDirEntry.insert(0, self.ArchiveDirectory)
            archiveDirEntry.pack(side=tk.LEFT, pady=5)

            rightPanel = tk.LabelFrame(self.root, text="Actions", padx=10, pady=10, width=max)
            rightPanel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=10)

            tk.Button(rightPanel, text="Load New Sessions", command=lambda: self.LoadNewSessions()) \
                .pack(fill=tk.X, pady=5)
            self.teamCombobox = ttk.Combobox(rightPanel, values= list(["None Selected"]) + list(self.sessions.sessions["VETeamLeads"].keys()), state="readonly")
            self.teamCombobox.current(0)
            self.teamCombobox.pack(fill=tk.X, pady=5)
            
            tk.Button(rightPanel, text="Create VE Count", command=lambda: self.CreateVECount())\
                .pack(fill=tk.X, pady=5)
            
            tk.Button(rightPanel, text="Create Session Stats", command=lambda: self.CreateSessionStats(), state="disabled").pack(fill=tk.X, pady=5)
        
        except Exception as e:
            logger.error(f"Error occurred while initializing GUI: {e}")

        self.root.mainloop()
        logger.info(f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}: Finished')
    def setDirectories(self, importDir, outputDir, archiveDir):
        self.ImportDirectory = os.path.join('.', importDir)
        self.OutputDirectory = os.path.join('.', outputDir)
        self.ArchiveDirectory = os.path.join('.', archiveDir)

        logger.info(f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}: Setting directories')
        if not os.path.exists(self.ImportDirectory):
            logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Import directory {self.ImportDirectory} does not exist. Creating it.")
            try:
                os.mkdir(self.ImportDirectory)
            except Exception as e:
                logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while creating import directory: {e}")
        if not os.path.exists(self.OutputDirectory):
            logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Output directory {self.OutputDirectory} does not exist. Creating it.")
            try:
                os.mkdir(self.OutputDirectory)
            except Exception as e:
                logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while creating output directory: {e}")
        if not os.path.exists(self.ArchiveDirectory):
            logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Archive directory {self.ArchiveDirectory} does not exist. Creating it.")
            try:
                os.mkdir(self.ArchiveDirectory)
            except Exception as e:
                logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while creating archive directory: {e}")

    def UpdateTeamCombobox(self):
        logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Updating team combobox with new session data")
        try:
            self.teamCombobox['values'] = list(["None Selected"]) + list(self.sessions.sessions["VETeamLeads"].keys())
            self.teamCombobox.current(0)
        except Exception as e:
            logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while updating team combobox: {e}")

    def LoadNewSessions(self):
        logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Loading new sessions...")
        try:
            self.sessions.ReadSessionJson(self.ImportDirectory, self.ArchiveDirectory)
            self.UpdateTeamCombobox()
        except Exception as e:
            logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while loading new sessions: {e}")

    def CreateVECount(self):
        logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Creating VE count...")
        try:
            self.sessions.OutputVEList(self.teamCombobox.get(), self.OutputDirectory, f"VE List{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        except Exception as e:
            logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while creating VE count: {e}")
    def CreateSessionStats(self):
        logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Creating session stats...")
        try:
            logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}:....Not Implemented Yet")
        except Exception as e:
            logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while creating session stats: {e}")
   
    def OpenDirectory(self, path):
        logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Opening directory: {path}")
        try:
            if os.path.exists(path):
                logger.info(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Directory exists. Opening...")
                os.startfile(path)
        except Exception as e:
            logger.error(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: Error occurred while opening directory: {e}")


if __name__ == '__main__':
    main()