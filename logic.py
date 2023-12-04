from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPalette, QColor
from gui import *
import os
import csv


class Logic(QMainWindow, Ui_MainWindow):
    """
    This class handles all the logic for the GUI.
    """
    
    def __init__(self) -> None:
        """
        This function initializes the GUI and sets up the buttons.
        """
        
        # Set up GUI and initialize private variables
        super().__init__()
        self.setupUi(self)                          
        self.__leaguecsv = ""
        self.__procsv = ""
        self.__teams = []
        self.__pro_file = False
        self.__league_file = False
        self.__sort_order = "↑"
        self.__group_order = "↑"
        self.__elligible_files = 0
        
        # Get all files in directory and add all CSV files to combo/selection boxes
        self.__files = os.listdir()                 
        for file in self.__files:                   
            if file.endswith(".csv"):
                self.combo_leaguecsv.addItem(file)
                self.combo_procsv.addItem(file)
                self.__elligible_files += 1
        
        # If there are not enough CSV files, display error message
        if self.__elligible_files < 1:                 
            self.label_league_exception.setText("Not enough CSV files in directory")    
            self.label_pros_exception.setText("Not enough CSV files in directory")
        
        # Set up buttons        
        self.button_enter.clicked.connect(lambda : self.enter())
        self.button_apply_sort.clicked.connect(lambda : self.apply())
        self.button_sort_direction.clicked.connect(lambda : self.direction("sort"))
        self.button_apply_team.clicked.connect(lambda : self.apply_teams())
        self.button_group_direction.clicked.connect(lambda : self.direction("group"))
                           
    def enter(self) -> None:
        """
        Method to handle the enter button.  Checks if the files are valid and if so, fills the list.

        :raises Exception: the pro csv file is invalid and the league csv file is valid
        :raises Exception: the league csv file is invalid and the pro csv file is valid
        :raises Exception: both the pro csv file and the league csv file are invalid
        """
        
        # Get the file names from the combo boxes and clear the exception labels
        self.__leaguecsv = self.combo_leaguecsv.currentText()
        self.__procsv = self.combo_procsv.currentText()
        self.label_pros_exception.setText("")
        self.label_league_exception.setText("")
        
        # Check if the files are valid and if not, display error message and set pro_file to False
        # If the files are valid, set pro_file to True and fill the list and combo box with the teams
        try:
            with open(self.__procsv) as csvfile:
                reader = csv.reader(csvfile)
                first_row = next(reader)
                if first_row != ["RK","TIERS","PLAYER NAME","TEAM","POS","BYE WEEK","AGE","SOS SEASON","ECR VS. ADP"]:
                    raise Exception("Invalid League CSV File")
        except:
            self.label_pros_exception.setText("Invalid Pro CSV File")
            self.__pro_file = False
            try:
                with open(self.__leaguecsv) as csvfile:
                    reader = csv.reader(csvfile)
                    first_row = next(reader)
                    if first_row != ["ID","Last Name","First Name","Team ID","Team Name","Status","Status Details","Position","Eligible Positions","Image"]:
                        raise Exception("Invalid League CSV File")
            except:
                self.label_league_exception.setText("Invalid League CSV File")
                self.__league_file = False
        else:
            self.__pro_file = True
            try:
                with open(self.__leaguecsv) as csvfile:
                    reader = csv.reader(csvfile)
                    first_row = next(reader)
                    if first_row != ["ID","Last Name","First Name","Team ID","Team Name","Status","Status Details","Position","Eligible Positions","Image"]:
                        raise Exception("Invalid League CSV File")
            except:
                self.label_league_exception.setText("Invalid League CSV File: Continuing with Pro CSV File")
                self.__league_file = False
                self.combo_team.clear()
                self.combo_team.update()    
                self.combo_team.addItems(self.get_teams())
                self.fill_list()
            else:
                self.__league_file = True
                self.combo_team.clear()
                self.combo_team.update()    
                self.combo_team.addItems(self.get_teams())
                self.fill_list()
        
    def apply(self) -> None:
        """
        Method to handle the apply button for both sort and group. Also refills list before applying.
        """
        
        # If the files have been picked, clear the list, refill the list, sort, and group
        if self.__pro_file:
            self.clear_list()
            self.fill_list()
            self.sort()
            self.group()
            
    def direction(self, direction_selection) -> None:
        """
        Method to handle the direction buttons for both sort and group.
        """
        
        # If the files have been picked, change the direction of the button
        if self.__pro_file == True:
            if self.button_sort_direction.text() == "↓" and direction_selection == "sort":
                self.button_sort_direction.setText("↑")
                self.__sort_order = "↑"
            elif self.button_sort_direction.text() == "↑" and direction_selection == "sort":
                self.button_sort_direction.setText("↓")
                self.__sort_order = "↓"
            elif self.button_group_direction.text() == "↓" and direction_selection == "group":
                self.button_group_direction.setText("↑")
                self.__group_order = "↑"
            elif self.button_group_direction.text() == "↑" and direction_selection == "group":
                self.button_group_direction.setText("↓")
                self.__group_order = "↓"
    
    def apply_teams(self) -> None:
        """
        Method to handle the apply button for the teams combo box.
        """
        
        # If the files have been picked, clear the list and refill the list with the correct team
        if self.__pro_file == True:
            self.clear_list()
            self.fill_list()
    
    def sort(self) -> None:
        """
        Method to handle the sorting of the list. 
        """
        
        # If the files have been picked, sort the list based on the combo box selection
        if self.__pro_file == True:
            order = Qt.SortOrder.AscendingOrder if self.__sort_order == "↑" else Qt.SortOrder.DescendingOrder
            if self.combo_sort.currentText() == "Name":
                self.list_players.model().sort(0, order)
            elif self.combo_sort.currentText() == "Rank":
                self.list_players.model().sort(3, order)
            elif self.combo_sort.currentText() == "Stars":
                self.list_players.model().sort(5, order)
            elif self.combo_sort.currentText() == "ECR vs ADP":
                self.list_players.model().sort(6, order)
            elif self.combo_group.currentText() == "None":
                pass
    
    def group(self) -> None:
        """
        Method to handle the grouping of the list. Uses the stable sort algorithm to maintain precedence of the sort over the group.
        """
        
        # If the files have been picked, group the list based on the combo box selection
        if self.__pro_file == True:
            order = Qt.SortOrder.AscendingOrder if self.__group_order == "↑" else Qt.SortOrder.DescendingOrder
            if self.combo_group.currentText() == "Team":
                self.list_players.model().sort(7, order)
            elif self.combo_group.currentText() == "Position":
                self.list_players.model().sort(1, order)
            elif self.combo_group.currentText() == "Age":
                self.list_players.model().sort(2, order)
            elif self.combo_group.currentText() == "Bye Week":
                self.list_players.model().sort(4, order)
            elif self.combo_group.currentText() == "Stars":
                self.list_players.model().sort(5, order)
            elif self.combo_group.currentText() == "None":
                pass

    def fill_list(self) -> None:
        """
        Method to fill the list with the players from the league csv file.
        """
        
        # Creates a new model, sets the headers, and sets the model to the list
        self.__model = QStandardItemModel()
        self.__model.setHorizontalHeaderLabels(["Name", "Position", "Age", "Rank", "Bye", "Stars", "ECR/ADP", "Team"])
        self.list_players.setModel(self.__model)

        # Opens the league csv file and adds the players to the list 
        if self.__league_file == True:
            with open(self.__leaguecsv, newline='') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    if ((row[4] != "Team Name" and 
                        (self.combo_team.currentText() == "All Rostered Players" or 
                        self.combo_team.currentText() == "All Unrostered Players" or
                        self.combo_team.currentText() == "All Players")) or 
                        row[4] == self.combo_team.currentText()):
                            
                        new_player = Player(self.__procsv, row[2] + " " + row[1], row[8])
                        row = []
                        for j, item in enumerate(new_player.get_list()):
                            if j in [2, 3, 4, 5, 6]:
                                if item != '-' and item != '':
                                    number_item = QStandardItem()
                                    number_item.setData(int(item), Qt.ItemDataRole.DisplayRole)
                                    row.append(number_item)
                                else:
                                    row.append(QStandardItem('0'))
                            else:
                                row.append(QStandardItem(str(item)))
                        self.__model.appendRow(row)
        
        # If the combo box is set to "All Unrostered Players" or "All Players", add the players from the pro csv file            
        if self.combo_team.currentText() == "All Unrostered Players" or self.combo_team.currentText() == "All Players":
            with open(self.__procsv, newline='') as file:
                reader = csv.reader(file)
                new_player_list = []
                model_list = [self.__model.item(i, 0).text() for i in range(self.__model.rowCount())]
                for row in reader:
                    if row[2] not in [i for i in model_list] and row[2] != [i for i in model_list] and row[2] != "PLAYER NAME":
                        new_player = Player(self.__procsv, row[2])
                        row = []
                        for j, item in enumerate(new_player.get_list()):
                            if j in [2, 3, 4, 5, 6]:
                                if item != '-' and item != '':
                                    number_item = QStandardItem()
                                    number_item.setData(int(item), Qt.ItemDataRole.DisplayRole)
                                    row.append(number_item)
                                else:
                                    row.append(QStandardItem('0'))
                            else:
                                row.append(QStandardItem(str(item)))
                        new_player_list.append(row)
                        
                # If the combo box is set to "All Unrostered Players", clear the list and reset the headers
                if self.combo_team.currentText() == "All Unrostered Players":
                    self.clear_list()
                    
                # Add the players from the pro csv file to the list
                for i in range(len(new_player_list)):
                    self.__model.appendRow(new_player_list[i])
        
        
        # Stretch all columns to fit and then resize the first column to fit the text
        self.list_players.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.list_players.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                    
    def clear_list(self) -> None:
        """
        Method to clear the list.
        """
        
        # Clears the list and resets the headers
        self.list_players.model().clear()
        self.list_players.model().setHorizontalHeaderLabels(["Name", "Position", "Age", "Rank", "Bye", "Stars", "ECR/ADP", "Team"])
           
    def get_teams(self) -> list:
        """
        Method to get the teams from the league csv file.

        :return self.__teams: list of teams
        """
        
        self.__teams = []
        if self.__league_file == False:
            self.__teams.append("All Players")
            pass
        else:
            with open(self.__leaguecsv, "r") as file:
                for line in file:
                    if line.split(",")[4][1:-1] not in self.__teams and line.split(",")[4] != '"Team Name"':
                        self.__teams.append(line.split(",")[4][1:-1])
            self.__teams.append("All Rostered Players")
            self.__teams.append("All Unrostered Players")
            self.__teams.append("All Players")
        
        return self.__teams
    
class Player:
    """
    This class handles all the logic for the players.
    """
    
    def __init__(self, pro_csv, name, position = "") -> None:
        """
        Method to initialize the player class.
        
        :param pro_csv: pro csv file
        :param name: name of player
        :param position: position of player
        """
        
        # Initialize private variables
        self.__name = ""
        self.__pro_csv = pro_csv
        self.__position = ""
        self.__age = ""
        self.__rank = ""
        self.__bye = ""
        self.__stars = ""
        self.__ecrvadp = ""
        self.__team = ""
        
        # Search the pro csv file for the player and set the variables. If the player is not found, set the variables to 0 or unknown
        with open(self.__pro_csv, "r") as file:
            for line in file:
                if line.split(",")[2][1:-1] == name or name in line.split(",")[2][1:-1]:
                    self.__age = line.split(",")[6][1:-1]
                    self.__rank = line.split(",")[0][1:-1]
                    self.__bye = line.split(",")[5][1:-1]
                    self.__stars = line.split(",")[7][1]
                    self.__ecrvadp = line.split(",")[8][1:-2]
                    self.__team = line.split(",")[3]
                    self.__name = line.split(",")[2][1:-1]
                    self.__position = line.split(",")[4][1:-1]
                    temp = ""
                    for x in self.__position:
                        if x.isalpha():
                            temp += x
                    self.__position = temp   
                    break
                elif line.split(",")[2][1:-1] != name or name not in line.split(",")[2][1:-1]:
                    self.__age = "0"
                    self.__rank = "0"
                    self.__bye = "0"
                    self.__stars = "0"
                    self.__ecrvadp = "0"
                    self.__team = "unknown"
                    self.__name = name
                    self.__position = position
                    if self.__position == "DEF":
                        self.__position = "DST"
                    
    def get_list(self) -> list:
        """
        Method to get the list of variables.

        :return: list of variables
        """
        return [self.__name, self.__position, self.__age, self.__rank, self.__bye, self.__stars, self.__ecrvadp, self.__team]