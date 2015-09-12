--
-- Table definitions for the tournament project.
-- The tournament database serves as the implementation of a Swiss Tournament,
-- for Udacity Full-Stack Nanodegree Project #2.
--

-- Create and connect to tournament database, drop it if one already exists.
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

-- Connect to tournament database
\c tournament;

-- players table
CREATE TABLE players (  id SERIAL PRIMARY KEY,
                        name TEXT );


-- tournaments table
CREATE TABLE tournaments (  id SERIAL PRIMARY KEY,
                            name TEXT );

-- Initialize tournaments table by inserting a default tournament
INSERT INTO tournaments ( name ) VALUES ( 'Tournament 1' );


-- register table holds players and tournaments they are registed in
-- it also tracks each registered player's points and number of byes 
CREATE TABLE register ( tournament_id INTEGER REFERENCES tournaments(id),
                        player_id     INTEGER REFERENCES players(id),
                        wins          INTEGER DEFAULT 0,
                        points        INTEGER DEFAULT 0,
                        byes          INTEGER DEFAULT 0,
                        PRIMARY KEY(tournament_id, player_id) 
                     );


-- matches table
CREATE TABLE matches (  id            SERIAL PRIMARY KEY,
                        tournament_id INTEGER REFERENCES tournaments(id),
                        winner_id     INTEGER REFERENCES players(id),
                        loser_id      INTEGER REFERENCES players(id),
                        tied          BOOLEAN DEFAULT false
                     );


-- View to query number of matches
CREATE VIEW matches_count AS
    SELECT register.tournament_id, register.player_id, COUNT( matches ) as matches_count
    FROM   register
    LEFT JOIN matches ON
        (register.tournament_id = matches.tournament_id) AND
        (
            (register.player_id = matches.winner_id) OR
            (register.player_id = matches.loser_id)
        )
    GROUP BY
        register.tournament_id, register.player_id
    ORDER BY matches_count DESC;


-- View on opponents of each player
CREATE VIEW opponents AS
    SELECT  register.tournament_id, register.player_id, matches.loser_id AS opponent_id
    FROM    register
    JOIN    matches ON
        (register.tournament_id = matches.tournament_id) AND
        (register.player_id = matches.winner_id)
    UNION
    SELECT  register.tournament_id, register.player_id, matches.winner_id AS opponent_id
    FROM    register
    JOIN    matches ON
        (register.tournament_id = matches.tournament_id) AND
        (register.player_id = matches.loser_id);


-- View on OMW (Opponent Match Wins) which shows total points for the opponents
CREATE VIEW opponents_points AS
    SELECT opponents.tournament_id, opponents.player_id, SUM( register.points ) AS opponents_points
    FROM   opponents
    JOIN   register ON
        (opponents.tournament_id = register.tournament_id) AND
        (opponents.opponent_id = register.player_id)
    GROUP BY opponents.tournament_id, opponents.player_id;


-- View to query player standings, ordered by number of points and opponents points
CREATE VIEW standings AS
    SELECT  register.player_id  AS id,
            players.name        AS name,
            register.wins       AS wins,
            COUNT( matches )    AS matches,
            register.byes       AS byes
    FROM   register
    LEFT JOIN players ON
        (register.player_id = players.id)
    LEFT JOIN matches ON
        (register.tournament_id = matches.tournament_id) AND
        (
            (register.player_id = matches.winner_id) OR
            (register.player_id = matches.loser_id)
        )
    LEFT JOIN opponents_points ON
        (register.tournament_id = opponents_points.tournament_id) AND
        (register.player_id = opponents_points.player_id)
    GROUP BY
        register.tournament_id, register.player_id, players.name, opponents_points.opponents_points

    ORDER BY
        register.points DESC, 
        opponents_points.opponents_points DESC;
