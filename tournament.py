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
    """Remove all the match records from the database for the given tournament."""
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
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute( "SELECT COUNT( player_id ) FROM register WHERE tournament_id = (%s)", (tournament_id, ) )
    result = c.fetchall()
    db.close()
    return result[0][0]  


def registerPlayer(name, tournament_id = 1):
    """Adds a player to the tournament database for the specified tournament_id.
    The players as well as register tables will be modified to register this player for the tournament.
   
    Args:
      name: the player's full name (need not be unique).
      tournament_id: the tournament that player is registred in. Default is 'Tournament 1'
    """
    db = connect()
    c = db.cursor()
    # Insert player into the players table
    c.execute( "INSERT INTO players ( name ) VALUES ( (%s) ) RETURNING id", (name, ))
    db.commit()
    # Use the retuned player_id to insert the player_id and tournament_id into the register table
    player_id = c.fetchall()[0][0]
    c.execute( "INSERT INTO register ( tournament_id, player_id ) VALUES ( %s, %s )", (tournament_id, player_id) )
    db.commit()
    db.close()    


def playerStandings(tournament_id = 1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    # Insert player into the players table
    c.execute( "SELECT id, name, wins, matches FROM standings" )
    result = c.fetchall()
    db.close()    
    return result


def reportMatch(winner, loser, tied = 'false', tournament_id = 1):
    """Records the outcome of a single match between two players.

    Args:
      winner: the id number of the player who won
      loser:  the id number of the player who lost
      tie:    boolean that denotes if the match was a tie
      tournament_id: id of the tournament for this match
    """
    db = connect()
    c = db.cursor()
    # Insert win/lose/tie info into the matches table
    sql_insert = "INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( %s, %s, %s, %s )"
    #print sql_insert
    c.execute( sql_insert, (tournament_id, winner, loser, tied) )
    # Update score in the register table for win/lose/tie
    sql = '''
    UPDATE register SET score = score + {points} WHERE tournament_id = {t_id} AND player_id = {p_id}  
    '''
    sql_update = sql.format(
        points = str(POINTS_FOR_WIN),
        t_id   = str(tournament_id),
        p_id   = str(winner)
    )
    #print sql_update
    c.execute(sql_update)
    db.commit()
    db.close()    

 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


