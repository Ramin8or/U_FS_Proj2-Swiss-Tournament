#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

POINTS_FOR_TIE = 1
POINTS_FOR_WIN = 3

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id = 1):
    """Remove all the match records from the database for the given tournament.
    Arg:
        tournament_id: denotes the tournament to delete matches from (default is 'Tournament 1')
    """
    db = connect()
    c = db.cursor()
    c.execute( "DELETE FROM matches WHERE tournament_id = (%s)", (tournament_id, ) )
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    # Delete player information from matches, register, and players tables
    c.execute( "DELETE FROM matches" )
    c.execute( "DELETE FROM register" )
    c.execute( "DELETE FROM players" )
    db.commit()
    db.close()    


def countPlayers(tournament_id = 1):
    """Returns the number of players currently registered in a tournament.
    Arg:
        tournament_id: denotes the tournament (default is 'Tournament 1')
    """
    db = connect()
    c = db.cursor()
    c.execute( "SELECT COUNT( player_id ) AS player_count FROM register WHERE tournament_id = (%s)", (tournament_id, ) )
    result = c.fetchall()
    db.close()
    return result[0][0]  


def registerPlayer(name, tournament_id = 1):
    """Adds a player to the tournament database for the specified tournament_id.
    The players as well as register tables will be modified to register this player for the tournament.
   
    Args:
      name: the player's full name (need not be unique).
      tournament_id: the tournament that player will be registred in. Default is 'Tournament 1'
    """
    db = connect()
    c = db.cursor()
    # Insert player into the players table
    c.execute( "INSERT INTO players ( name ) VALUES ( (%s) ) RETURNING id", (name, ))
    db.commit()
    # Use the retuned id to insert the player_id and tournament_id into the register table
    player_id = c.fetchall()[0][0]
    c.execute( "INSERT INTO register ( tournament_id, player_id ) VALUES ( %s, %s )", (tournament_id, player_id) )
    db.commit()
    db.close()    


def playerStandings(tournament_id = 1):
    """Returns a list of the players and their win records, sorted by points from wins/ties.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.
    
    Arg:
        tournament_id: denotes the tournament for playerStandings (default is 'Tournament 1')
    
    Returns:
      A list of tuples, each of which contains (id, name, points, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        points: the number of points from matches the player has won or tied
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    # Return the play standings from the standings view. See tournament.sql for the definition.
    c.execute( "SELECT id, name, points, matches FROM standings" )
    result = c.fetchall()
    db.close()    
    return result


def reportMatch(winner, loser, tied = False, tournament_id = 1):
    """Records the outcome of a single match between two players.

    Args:
      winner: the id number of the player who won
      loser:  the id number of the player who lost
      tied:   boolean that denotes if the match was a tie
      tournament_id: id of the tournament for this match
    Note:
      if winner and loser are the same player, it signifies a Bye Game
      and the player will get an automatic win, but the match will not 
      be registered in the register table
    """
    db = connect()
    c = db.cursor()
    tied_match = ('true' if tied else 'false') 
    # Insert win/lose/tie info into the matches table, except if the same
    # player is specified for winner and loser. This case is a Bye Game.
    if (winner != loser):
        sql_insert = '''
        INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( %s, %s, %s, %s )
        '''
        c.execute( sql_insert, (tournament_id, winner, loser, tied_match) )

    # Update points in the register table for win or tie
    sql = '''
    UPDATE register SET points = points + {add_points} WHERE tournament_id = {t_id} AND player_id = {p_id}  
    '''
    if (tied == False):
        # If not a tied game, the winner gets POINTS_FOR_WIN points
        sql_update = sql.format(
            add_points = str(POINTS_FOR_WIN),
            t_id   = str(tournament_id),
            p_id   = str(winner)
        )
        c.execute(sql_update)
    else:
        # For a tied match, both players get POINTS_FOR_TIE points
        sql_update = sql.format(
            add_points = str(POINTS_FOR_TIE),
            t_id   = str(tournament_id),
            p_id   = str(winner)
        )
        c.execute(sql_update)
        sql_update = sql.format(
            add_points = str(POINTS_FOR_TIE),
            t_id   = str(tournament_id),
            p_id   = str(loser)
        )
        c.execute(sql_update)
    db.commit()
    db.close()    


def pickNextPlayer(standings, picked_already):
    """Returns the index of next available player
   
    Arg:
      standings: list returned from playerStandings() function
      picked_already: list of booleans that denote whether the index in 
                       standings has already been picked. 

    Returns:
      returns the index of first player in standings that has not been picked
      -1 is returned if there is no more player left to select
      it also sets the picked_already[index] to True
    """
    for index in range(0, len(standings)):
        if picked_already[index] == False:
            picked_already[index] = True
            return index
    return -1


def swissPairings(tournament_id = 1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Arg:
      tournament_id: id of the tournament to perform swiss pairing for

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    swiss_pairings = []
    standings = playerStandings(tournament_id)
    # paired_already is a list of booleans that denote if the corresponding index
    # in standings has already been paired
    paired_already   = [False] * len(standings)

    while True:
        player_1 = pickNextPlayer(standings, paired_already)
        if player_1 == -1:
            break 
        player_2 = pickNextPlayer(standings, paired_already)
        if player_2 == -1:
            print "Player: " + standings[player_1][1] + " is getting a Bye Game (paired with self)"
            player_2 = player_1 
        swiss_pairings.append(
            (
                standings[player_1][0], 
                standings[player_1][1],
                standings[player_2][0],
                standings[player_2][1]
            )
        )
    return swiss_pairings



