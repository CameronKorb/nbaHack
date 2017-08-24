# nbaHack

This repository was used by the team Big Baller Brains in order to create a solution for the bonus question of the 2017 NBA Hackathon application. This code should not be used by others because that violates the trust that NBA has that you will come up with your own solution.

We utililized pandas for virtually all of our calucations in this project.

Are basic strategy in determining when teams were eliminted from the playoffs went as followed:
- Calculate the total wins of each team and organize them by conference.
- Determine the mininum number of games that teams in each conference would have needed to win in order to make the playoffs (equal to the number of wins of the 8th best record in each conference).
- At everyday during the season calcualte how many possible games each team could win. 
- Determine elimination dates when the number of possible games a team could win is less than the number they needed.
- Deal with tie breakers. Because we only had to figure out which teams made the playoffs and not worry about seeding this wasn't too difficult, and in fact because of the rule change in 2016, we only needed to use the first tie breaker rule. Better head to heat record. This settled the only tie that mattered between the Heat and the Bulls. Further tie breakers could be added pretty straightforwardly if need be.

All of the code for the project is include in the elimination.py file, config.py contains constats used in the code.
The Input file includes the inputs we used, which were taken directly from the file provided by the NBA. 
The output file contains our solution in elimination_dates.csv. 

-Big Baller Brains
