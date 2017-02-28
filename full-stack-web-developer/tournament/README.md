Tournament Results
==================

##Dependencies

1. Python must be installed in the environment.
2. vagrant virtual machine

##Directory Structure 
  ```
 \
 |--tournament.py
 |--tournament.pyc
 |--tournament.sql
 |--tournament_test.py
  ```
  
##Execution
 ```
vagrant up
vagrant ssh
dropdb --if-exists tournament
createdb tournament
psql tournament -f /vagrant/tournament/tournament.sql
cd /vagrant/tournament
python tournament_test.py
 ```

This command will execute all the following tests:
 ```
1. Old matches can be deleted.
2. Player records can be deleted.
3. After deleting, countPlayers() returns zero.
4. After registering a player, countPlayers() returns 1.
5. Players can be registered and deleted.
6. Newly registered players appear in the standings with no matches.
7. After a match, players have updated standings.
8. After one match, players with one win are paired.
Success!  All tests pass!
 ```
  
