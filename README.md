# U_FS_Proj2-Swiss-Tournament
Udacity Full-Stack Project 2: Swiss Tournament 

# Intoduction
This project is the second project for Udacity Full-Stack Nanodegree. For more information please refer to the specifications provided here:

https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true

The project uses a PostgreSQL database to record tournament information such as players, matches, points etc. The schema is provided in *tournament.sql* file. The Python code in *tournament.py* accesses the database and performs a Swiss Tournament Pairing among the players. There is also a test file, *tournament_test.py* that excercise the features provided by this project.

# Extra credit features implemented
Beyond the basic requirements, the following features have also been implemented:
- Bye games: when number of players is uneven, one player gets a bye game which is an automatic win
- Tied games: reportMatch() has an additional default parameter that denotes a draw
- Opponent Match Wins: when two players have the same number of points a tie breaker is used by looking at OMW. The player who has played against opponents with more points wins.
- Support for more than one turnament
- 3 points are earned for each win, and 1 point for a draw. No points are given for a loss.

# Tournament Database



