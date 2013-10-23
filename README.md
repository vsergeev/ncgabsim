# ncgabsim

## Simulating

Configure the ncgabsim simulation by selecting the simulation at the top of `ncgabsim.py`.

Run ncgabsim with: `python2 ncgabsim.py`.

It will produce data in `data/` and a log in `logs/` for each simulation.

## Processing and Plotting

Post-process and plot ncgabsim simulation results with `stats_process.py`. Run:

`$ python2 stats_process.py SpecialPrefix data/*`

to plot pretty plots to your screen and also save the plots to `CustomPrefix-availability.eps` and `CustomPrefix-delay.eps`.

