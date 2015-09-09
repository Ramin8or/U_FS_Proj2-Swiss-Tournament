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
-- it also tracks each registered player score and number of bye games
CREATE TABLE register ( tournament_id INTEGER REFERENCES tournaments(id),
                        player_id     INTEGER REFERENCES players(id),
                        score         INTEGER DEFAULT 0,
                        bye_games     INTEGER DEFAULT 0,
                        PRIMARY KEY(tournament_id, player_id) );

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

-- View on OMW (Opponent Match Wins) which show total scores for the opponents
CREATE VIEW opponents_score AS
    SELECT opponents.tournament_id, opponents.player_id, SUM( register.score ) AS opponents_score
    FROM   opponents
    JOIN   register ON
        (opponents.tournament_id = register.tournament_id) AND
        (opponents.opponent_id = register.player_id)
    GROUP BY opponents.tournament_id, opponents.player_id;

-- View to query player standings
CREATE VIEW standings AS
    SELECT  register.player_id,
            players.name,
            register.score,
            COUNT( matches ) as total_matches
    FROM   register
    LEFT JOIN players ON
        (register.player_id = players.id)
    LEFT JOIN matches ON
        (register.tournament_id = matches.tournament_id) AND
        (
            (register.player_id = matches.winner_id) OR
            (register.player_id = matches.loser_id)
        )
    LEFT JOIN opponents_score ON
        (register.tournament_id = opponents_score.tournament_id) AND
        (register.player_id = opponents_score.player_id)
    GROUP BY
        register.tournament_id, register.player_id, players.name, opponents_score.opponents_score

    ORDER BY
        register.score DESC, 
        opponents_score.opponents_score DESC;

-- Initial data for testing
--INSERT INTO players ( name ) VALUES ( 'one' );
--INSERT INTO players ( name ) VALUES ( 'two' );
--INSERT INTO players ( name ) VALUES ( 'three' );
--INSERT INTO players ( name ) VALUES ( 'four' );
--INSERT INTO players ( name ) VALUES ( 'five' );
--INSERT INTO players ( name ) VALUES ( 'six' );
--
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,1,4 );
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,2,3 );
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,3,4 );
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,4,0 );
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,5,4 );
--INSERT INTO register ( tournament_id, player_id, score ) VALUES ( 1,6,1 );
--
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,1,2,false );
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,3,4,false );
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,5,6,true  );
--
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,1,3,true  );
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,2,4,false );
--INSERT INTO matches ( tournament_id, winner_id, loser_id, tied  ) VALUES ( 1,5,6,false );
