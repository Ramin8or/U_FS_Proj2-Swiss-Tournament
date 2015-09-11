#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

# dbapi library to connect to PostgreSQL database
import psycopg2

from collections import defaultdict

# Global constanst for points. Tie earns 1 point, Win earns 3
TIE_POINTS = 1
WIN_POINTS = 3

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id = 1):
    """Remove all the match records from the database for the given tournament.
    Arg:
      tournament_id: denotes the tournament to delete matches from
    """
    db = connect()
    c = db.cursor()
    c.execute( "DELETE FROM matches WHERE tournament_id = (%s)", 
        (tournament_id, )
    )
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
    sql = '''
    SELECT COUNT( player_id ) AS player_count 
        FROM register 
        WHERE tournament_id = (%s)
    '''
    c.execute(sql, (tournament_id, ))
    result = c.fetchall()
    db.close()
    return result[0][0]  


def registerPlayer(name, tournament_id = 1):
    """Adds a player to the tournament database in specified tournament_id.
   
    Args:
      name: the player's full name (need not be unique).
      tournament_id: the tournament default is 'Tournament 1'

    Returns:
      For testing purposes, the id of player is returned.
    """
    db = connect()
    c = db.cursor()
    # Insert player into the players table
    c.execute( "INSERT INTO players ( name ) VALUES ( (%s) ) RETURNING id", 
        (name, ))
    db.commit()
    # Using retuned id, insert player_id and tournament_id into register
    player_id = c.fetchall()[0][0]
    c.execute( 
        "INSERT INTO register ( tournament_id, player_id ) VALUES ( %s, %s )", 
        (tournament_id, player_id) 
    )
    db.commit()
    db.close() 
    return player_id   


def playerStandings(tournament_id = 1):
    """Returns list of players and win records, sorted by overall standings.

    The first entry in the list should be the player in first place, or player
    tied for first place if there is currently a tie.
    
    Arg:
      tournament_id: denotes the tournament (default is 'Tournament 1')
    
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of wins
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    # Return the player standings from the standings view. See tournament.sql.
    c.execute( "SELECT id, name, wins, matches FROM standings" )
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
      if winner and loser are the same player, it signifies a Bye Game.
    """
    db = connect()
    c = db.cursor()
    tied_match = ('true' if tied else 'false') 
    if (winner != loser):
        # Insert win/lose/tie info into the matches table.
        sql = '''
        INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) 
            VALUES ( %s, %s, %s, %s )
        '''
        c.execute( sql, (tournament_id, winner, loser, tied_match) )
    else:
        # For a bye game (winner == loser) update byes in register table.
        # Points/win for player will be updated but bye game won't 
        # appear in matches table.
        sql_update_bye = '''
        UPDATE register 
            SET byes = byes + 1 
            WHERE tournament_id = {t_id} AND player_id = {p_id}  
        '''
        c.execute(sql_update_bye, str(tournament_id), str(winner))
    # Update points in the register table for win or tie
    sql_update_points = '''
    UPDATE register 
        SET points = points + %s WHERE 
        tournament_id = %s AND player_id = %s  
    '''
    if (tied == True):
        # For a tied match, both players get an additional TIE_POINTS points
        c.execute(sql_update_points, 
            (str(TIE_POINTS), str(tournament_id), str(winner))
        )
        c.execute(sql_update_points, 
            (str(TIE_POINTS), str(tournament_id), str(loser))
        )
    else:
        # If not a tied game, the winner gets WIN_POINTS points
        c.execute(sql_update_points, 
            (str(WIN_POINTS), str(tournament_id), str(winner))
        )
        sql_update_wins = '''
        UPDATE register 
            SET wins = wins + 1 
            WHERE tournament_id = (%s) AND player_id = (%s)  
        '''
        c.execute(sql_update_wins,(str(tournament_id), str(winner)))
    db.commit()
    db.close()    


def getOpponents(tournament_id = 1):
    """Returns dictionary of players and opponents they have played against.

    Arg:
      tournament_id: denotes the tournament (default is 'Tournament 1')
    
    Returns:
      A list of tuples, each of which contains (player_id, opponent_id):
        player_id: the player's unique id (assigned by the database)
        opponent_id: the id of player who has been an opponent of player_id
    """
    db = connect()
    c = db.cursor()
    # Fetch opponents from opponents view in tournament.sql.
    sql = '''
        SELECT player_id, opponent_id FROM opponents 
        WHERE tournament_id = (%s)
    '''
    c.execute(sql, (tournament_id,))
    results = c.fetchall()
    db.close()
    # Create dictionary where key is player_id, value is list of opponents
    opponents_table = defaultdict(list)
    for row in results:
        opponents_table[row[0]].append(row[1])
    return opponents_table


def pickNextPlayer(standings, picked_already, opponents_list=[]):
    """Returns the index of next available player
   
    Arg:
      standings: list returned from playerStandings() function.
      picked_already: list of booleans that denote whether the index in 
                       standings has already been picked. 
      opponents_list: list of opponents that should not play against.

    Returns:
      Function sets the picked_already[index] to True, when player is picked
      returns the index into standings of player that is picked
      -1 is returned if there is no more player left to select
    """
    for index in range(0, len(standings)):
        if picked_already[index] == False:
            # Skip player if this player is in the opponents_list
            if standings[index][0] in opponents_list:
                continue
            # Return the index for this player, we're done
            picked_already[index] = True
            return index
    # If there are any unpicked players left, return the first one before giving up
    for index in range(0, len(picked_already)):
        if picked_already[index] == False:
            picked_already[index] = True
            return index
    # No one else left, giving up     
    return -1


def swissPairings(tournament_id = 1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    For an odd number of players, the last player will be paired with itself
    to denote a bye game. reportMatch() detects bye games when winner and
    loser is the same player.
  
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
    # playerStandings() returns list sorted by standing including tie breakers
    standings = playerStandings(tournament_id)
    # paired_table is list of booleans to denote if player at index is paired
    paired_table = [False] * len(standings)
    # opponents_table is a dictionary of players and their opponents
    opponents_table = getOpponents(tournament_id)
    # Do the Swiss Pairing
    while True:
        # Pick the top unpaired player
        player_1 = pickNextPlayer(standings, paired_table)
        if player_1 == -1:
            # No more players to match, we are done
            break
        # Get the player_id from standings 
        player1_id = standings[player_1][0]
        # Get the list of opponents for this player
        opponents_list = opponents_table[player1_id]
        # Pick the next player in standings, avoid rematch using opponent_list
        player_2 = pickNextPlayer(standings, paired_table, opponents_list) 
        if player_2 == -1:
            # No one to pair with. Player gets a bye game (paired with itself)
            player_2 = player_1 
        # Append to swiss_parings results
        swiss_pairings.append(
            (standings[player_1][0], standings[player_1][1],
            standings[player_2][0], standings[player_2][1])
        )
    # We are done!
    return swiss_pairings


