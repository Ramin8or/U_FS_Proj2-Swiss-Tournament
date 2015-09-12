# U_FS_Proj2-Swiss-Tournament
Udacity Full-Stack Nanodegree Project 2: Swiss Tournament 

# Introduction
This project is the second project for Udacity Full-Stack Nanodegree. For more information on setting up the environment to run the project and the specifications please refer to [this document.](https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true)


The project uses a PostgreSQL database to record tournament information such as players, matches, tournaments etc. The database schema is provided in *tournament.sql* file. The Python code in *tournament.py* accesses the database to record play and match information as well as tracking player standings. It also performs a Swiss Tournament Pairing among the players. There is a test file, *tournament_test.py* that excercise the features provided by this project.

# Project files
- *tournament.sql* - this file is used to set up the tournament database schema
- *tournament.py* - this file is used to provide access to the database via a library of functions which can add, delete or query data in the database. 
- *tournament_test.py* - this is a client program which excercises functions written in the tournament.py module. 

# Setup and pre-requisites
- Install [Vagrant](https://www.vagrantup.com/) and [Virtual Box](https://www.virtualbox.org/)
- Get the tournament files mentioned above from this github project: (https://github.com/Ramin8or/U_FS_Proj2-Swiss-Tournament) 
- Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm)
- Launch the Vagrant VM from the vagrant directory, run "vagrant up" in the command line. Then connect to Vagrant VM by running "vagrant ssh"
- Create the tournament database by running psql, then issue command: \i tournament.sql
- Run tournament unit tests by running: "python tournament_test.py"

# Extra credit features implemented
Beyond the basic requirements, the following features have also been implemented:
1. Support for multiple tournaments
A tournament table is provided to track multiple tournaments. For compatibility purposes, all functions in *tournament.py* take a tournament_id as a default parameter that defaults to 'Tournament 1'.
2. Prevent rematches between players
This functionality is implemented via a View in the database that returns all the players and their opponents. This information is used in a dictionary to avoid pairing up players who have already played against each other.
3. Bye games
When there is an odd number of players, one player gets a bye game which is an automatic win. Players who already have had a bye game will not get a bye.
4. Tied games
reportMatch() takes an additional boolean parameter to denote if there was a draw. For compatibility purposes this parameter is a default param that defaults to false.
5. Opponent Match Wins
When two players have the same number of points, a tie breaker is used by looking at OMW. The player who has played against opponents with more points wins.
6. Points
3 points are earned for each win, and 1 point for a draw. No points are given for a loss. playerStandings() continues to report wins and number of matches, however, the standings are sorted by points earned and opponent win points.

# Tournament Database
Please refer to *tournament.sql* for more information. The tournament database consists of the following tables:
- **players:** stores id and name of each player
- **turnaments:** stores id and name of each tournament. A default value of 'Tournament 1' is always present.
- **register:** used to register each player in each tournament. To simplify SQL statements this table tracks the number of points earned from wins and ties, the number of wins, and the number of bye games. This information is updated when reportMatch() is called. Tracking points in this table simplifies the SQL queries for calculating player standings.
- **matches:** tracks win, loss, tie between two players in a tournament

In addition, there are views stored in this database that provide the following queries:
- Number of matches for each player in each tournament
- Opponents and opponent points for each player in each tournament
- Standings: this view is a list of all players ranked by their points. If two players have the same number of points, the information about the points for opponents they have won against is used as a tie breaker.

# Swiss Tournament Pairing
Since the database view for standings already provides a ranked list of players, the pairing is done simply by pairing up two players from top to bottom of rankings. If number of players are uneven, the last player gets a bye which is an automatic win. Rematches between players are prevented by fetching the opponent view which returns a table of players and their opponents. This information is used to skip pairing between players who have played against each other in previous rounds.

