# Automated NCAA Bracket Selection with Python
This is a python project to seed an NCAA Basketball Tournament Bracket. See [my post](https://ryangooch.github.io/Automated-Selection-Committee/) for more information on the underlying process.

## Requirements
The project was written with Python 3.5, although Python 2.x ought to be OK as well.

The following packages are required:

* [NumPy](http://www.numpy.org/)
* [pandas](http://pandas.pydata.org/)
* [openpyxl](https://openpyxl.readthedocs.io/en/default/)

Many thanks to those projects for making this one a lot easier!

## Usage
For now, this isn't something that would live on your Python path. Clone or download the repository, then copy bracket_picker.py to your working directory.

``` python
from bracket_picker import Bracketeer

b = Bracketeer()
```

If you want to use all the polls available to you, you can simply run the following code to calculate your tournament field.

``` python
b.get_tourney_teams()

b.final_68
```

This will print your 68 team field. If you want to put this on a bracket, you'll have to run one more method and then manually copy the field to the correct spots in the provided bracket template. This will hopefully be automated too in future!

``` python
b.fill_bracket()
```

And that's it! However, there are some functions in place to help you customize the selection process! At current, all available computer polls, and two human polls ([AP and Coaches Polls](http://www.espn.com/mens-college-basketball/rankings)) are used in the information. If you have a subset of polls you'd prefer, you can specify those. Additionally, you can formulate your own final rank calculation metric. An example is shown below.

``` python

from bracket_picker import Bracketeer

b = Bracketeer()

# Let's view the available polls
b.print_polls()

# Example Output:
# Index(['Team', 'Conf', 'WL', 'Rank', 'Mean', 'Trimmed', 'Median', 'StDev',
#       '7OT', 'AP', 'BBT', 'BIH', 'BUR', 'BWE', 'D1A', 'DAV', 'DC', 'DC2',
#       'DCI', 'DDB', 'DES', 'DII', 'DOK', 'DOL', 'EBP', 'ESR', 'FMG', 'FSH',
#       'HAS', 'KPI', 'KPK', 'KRA', 'LMC', 'LOG', 'MAS', 'MOR', 'NOL', 'PGH',
#       'PIG', 'POM', 'PRR', 'REW', 'RPI', 'RSL', 'RT', 'RTH', 'RTP', 'SAG',
#       'SEL', 'SFX', 'SMN', 'SMS', 'SP', 'SPW', 'STH', 'TPR', 'TRK', 'TRP',
#       'USA', 'WIL', 'WLK', 'WOB', 'WOL', ''],
#      dtype='object')

# Manually mark winners of auto bid slots by conference with dict

conference_winners = {conf:None for conf in b.get_conferences()}

conference_winners['OVC'] = 'Murray St'
conference_winners['BSo'] = 'Gardner Webb'
conference_winners['MVC'] = 'Bradley'
conference_winners['ASUN']= 'Liberty'

comp_polls = ['POM','7OT','SAG','NET','MAS']

def rank_calc(x, y) :
# Averages polls and weights computer over human 3 to 1
  if np.isnan(y) :
    return x
  else :
    return ((3 * x + y) / 4.)

b.get_tourney_teams(
    comp_polls = comp_polls,
    rank_calc_func = rank_calc,
    conf_winners=conference_winners
)

# print the top 16 teams
b.final_68.head(16)

# produce bracket text to copy to template
b.fill_bracket()
```

If you have any questions/issues/ideas for improvement, feel free to add them in the Issues. I hope you enjoy this project!









