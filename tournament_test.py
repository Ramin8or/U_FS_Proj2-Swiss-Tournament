#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

# Global constanst for points. Tie earns 1 point, Win earns 3
POINTS_FOR_TIE = 1
POINTS_FOR_WIN = 3

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != POINTS_FOR_WIN:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testByeGame():
    deleteMatches()
    deletePlayers()
    p1 = registerPlayer("1")
    p2 = registerPlayer("2")
    p3 = registerPlayer("3")
    p4 = registerPlayer("4")
    p5 = registerPlayer("5")
    pairings = swissPairings()
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return three pairs.")
    # Verify that there is one pairing with a player matched with itself (bye game)
    found_bye = False
    for each_tuple in pairings:
        (pid1, name1, pid2, name2) = each_tuple
        if pid1 == pid2:
            if found_bye == False:
                found_bye = True
            else:
                raise ValueError(
                    "There should only be a single bye game.")

    if found_bye == False:
        raise ValueError(
            "No bye game was scheduled.")

    print "9. Swiss pairing handles bye games for odd number of players."


def testNoRematch():
    deleteMatches()
    deletePlayers()
    p1 = registerPlayer("1")
    p2 = registerPlayer("2")
    p3 = registerPlayer("3")
    p4 = registerPlayer("4")
    p5 = registerPlayer("5")
    p6 = registerPlayer("6")

    # All odd number players tie each other
    reportMatch(p1, p3, True)
    reportMatch(p1, p5, True)
    reportMatch(p3, p5, True)
    reportMatch(p3, p1, True)
    reportMatch(p5, p1, True)
    reportMatch(p5, p3, True)

    # All even number players win each other
    reportMatch(p2, p4)
    reportMatch(p4, p2)
    reportMatch(p2, p6)
    reportMatch(p6, p2)
    reportMatch(p4, p6)
    reportMatch(p6, p4)

    # Verify that the top 3 players are even numbered, bottom 3 are odd
    standings = playerStandings()
    index = 0
    for row in standings:
        if index < 3:
            if (int(row[1]) % 2) != 0:
                raise ValueError("Top 3 players must be even numbered.")
        else:
            if (int(row[1]) % 2) == 0:
                raise ValueError("Bottom 3 players must be odd numbered.")
        index +=1
   
    # Verify that only odd vs. even pairs are matched, even though even players have higher points
    pairings = swissPairings()
    if len(pairings) != 3:
        raise ValueError(
            "For six players, swissPairings should return three pairs.")
    for each_tuple in pairings:
        (pid1, name1, pid2, name2) = each_tuple
        if (int(name1) + int(name2)) % 2 == 0:
            raise ValueError(
                "Only odd vs. even number players should have been matched.")

    print "10. No rematch is working properly when pairing players."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testByeGame()
    testNoRematch()
    print "Success!  All tests pass!"


