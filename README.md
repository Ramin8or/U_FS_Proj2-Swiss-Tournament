# U_FS_Proj2-Swiss-Tournament
Udacity Full-Stack Nanodegree Project 2: Swiss Tournament 

# Introduction
This project is the second project for Udacity Full-Stack Nanodegree. For more information on setting up the environment to run the project and the specifications please refer to this document:

https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true

The project uses a PostgreSQL database to record tournament information such as players, matches, tournaments etc. The database schema is provided in *tournament.sql* file. The Python code in *tournament.py* accesses the database to record play and match information as well as tracking player standings. It also performs a Swiss Tournament Pairing among the players. There is a test file, *tournament_test.py* that excercise the features provided by this project.

# Pre-requisite
- Install Vagrant and Python
- Clone this project 
- Launch the Vagrant VM, and run "vagrant up" in the command line. Then connect to Vagrant VM by running "vagrant ssh" 
- Run tournament unit tests by running: "python tournament_test.py"

# Extra credit features implemented
Beyond the basic requirements, the following features have also been implemented:
- Prevent rematches between players
- Bye games: when number of players is uneven, one player gets a bye game which is an automatic win
- Tied games: reportMatch() has an additional default parameter that denotes a draw
- Opponent Match Wins: when two players have the same number of points, a tie breaker is used by looking at OMW. The player who has played against opponents with more points wins.
- Support for more than one turnament
- 3 points are earned for each win, and 1 point for a draw. No points are given for a loss.

# Tournament Database
Please refer to *tournament.sql* for more information. The tournament database consists of the following tables:
- **players:** stores id and name of each player
- **turnaments:** stores id and name of each tournament. A default value of 'Tournament 1' is always present.
- **register:** used to register each player in each tournament. Also provides the running points and whether the player had a bye game. Points and bye games are recorded when matches are reported. Tracking points in this table simplifies the SQL queries for calculating player standings.
- **matches:** tracks win, loss, tie between two players in a tournament

In addition, there are views stored in this database that provide the following queries:
- Number of matches for each player in each tournament
- Opponents and opponent points for each player in each tournament
- Player Standings: this view is a list of players ranked by their points. If two players have the same number of points, the information about the points for opponents they have won against is used as a tie breaker.

# Swiss Tournament Pairing
Since the database view for PlayerStandings already provides a ranked list of players, the pairing is done simply by pairing up two players from top to bottom of rankings. If number of players are uneven, the last player gets a bye which is an automatic win. Rematches between players are prevented by fetching the opponent view which returns a table of players and their opponents. This information is used to skip pairing between players who have played against each other in previous rounds.

