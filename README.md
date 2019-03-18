# Automated NCAA Bracket Selection with Python
This is a python project to seed an NCAA Basketball Tournament Bracket. See [my post](https://ryangooch.github.io/Automated-Selection-Committee/) for more information on the underlying process.

## Requirements
The project was written with Python 3.7.

The following packages are required:

* [NumPy](http://www.numpy.org/)
* [pandas](http://pandas.pydata.org/)
* [openpyxl](https://openpyxl.readthedocs.io/en/default/)

Many thanks to those projects for making this one a lot easier!

## Usage
For now, this isn't something that would live on your Python path. Clone or download the repository, then import from the directory as needed (or work within the directory).

``` python
from metrics import Bracketeer

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

And that's it! 

However, there are some functions in place to help you customize the selection process! At current, all available computer polls, and two human polls ([AP and Coaches Polls](http://www.espn.com/mens-college-basketball/rankings)) are used in the information. If you have a subset of polls you'd prefer, you can specify those. Additionally, you can formulate your own final rank calculation metric. An example is shown below.

``` python

from metrics import Bracketeer

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
# First create empty dictionary, where keys are conference names and 
# teams are None
conference_winners = {conf:None for conf in b.get_conferences()}

# Populate with conference winners. At time of this writing, for 2019
# NCAA Tournament, those teams are:
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

## Ratings
The code above uses *rankings* data, not *ratings* data, and ultimately computes an arithmetic mean of the computer and human rankings to produce the final bracket. There is ongoing development, however, to incorporate ratings data, thus utilizing the actual values produced by the analytics instead of ordinal positions. It is likely that averaging or otherwise manipulating these numerical outputs is more appropriate than manipulating the ordinal data. However, it is also far less convenient. Ken Massey graciously puts out a composite of rankings data, which is used in the code above. To get the raw values, though, one needs to scrape the web pages, or otherwise use an API, then massage it into a consistent format. This is not straightforward and usually requires a bespoke function to do this, along with developing a key/value list to convert team names to a standardized set of names.

This is the goal of the more recent development in this project, along with some refactoring to make the code more modular and thus easier to add or remove functionality.

Currently, three ratings are supported: 
* [kenpom](https://kenpom.com/)
* [ESPN BPI](http://www.espn.com/mens-college-basketball/bpi)
* [Dokter Entropy](http://www.timetravelsports.com/colbb.html)

It is hoped that soon the [NET](https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings) and [Massey](https://www.masseyratings.com/cb/ncaa-d1/ratings) ratings will be incorporated, to provide a larger sample size, a more diverse set of trusted tools, and allow some more interesting analysis.

Current usage incorporates the three ratings above, and ignores human polls, since it is unclear whether averaging rankings with the aggregate ratings would produce a more valuable result.

```python
import numpy as np
import pandas as pd
from metrics import Bracketeer

b = Bracketeer()

# 2019 autobids
conference_winners = {conf:None for conf in b.get_conferences()}

conference_winners['OVC'] = 'Murray St'
conference_winners['BSo'] = 'Gardner Webb'
conference_winners['MVC'] = 'Bradley'
conference_winners['ASUN']= 'Liberty'
conference_winners['SC']  = 'Wofford'
conference_winners['MAAC']= 'Iona'
conference_winners['HL']  = 'N Kentucky'
conference_winners['NEC'] = 'F Dickinson'
conference_winners['CAA'] = 'Northeastern'
conference_winners['SL']  = 'N Dakota St'
conference_winners['WCC'] = "St Mary's CA"
conference_winners['PL'] = 'Colgate'
conference_winners['AEC'] = 'Vermont'
conference_winners['MEAC'] = 'NC Central'
conference_winners['B12'] = 'Iowa St'
conference_winners['MWC'] = 'Utah St'
conference_winners['SWAC'] = 'Prairie View'
conference_winners['BE'] = 'Villanova'
conference_winners['MAC'] = 'Buffalo'
conference_winners['BSC'] = 'Montana'
conference_winners['CUSA'] = 'Old Dominion'
conference_winners['ACC'] = 'Duke'
conference_winners["SLC"] = 'Abilene Chr'
conference_winners['WAC'] = 'New Mexico St'
conference_winners['P12'] = 'Oregon'
conference_winners['BWC'] = 'UC Irvine'
conference_winners['Ivy'] = 'Yale'
conference_winners['SEC'] = 'Auburn'
conference_winners['A10'] = 'St Louis'
conference_winners['SBC'] = 'Georgia St'
conference_winners['AAC'] = 'Cincinnati'
conference_winners['B10'] = 'Michigan St'

comp_polls = ['POM','DOK','EBP']

def rank_calc(x, y):
    if np.isnan(y) :
        return x
    else:
        return ((3 * x + y) / 4.)

b.get_tourney_teams(
    comp_polls = comp_polls,
    rank_calc_func = rank_calc,
    conf_winners = conference_winners,
    human_polls = False,
    use_metrics = True
)

b.final_68[['Team','Conf','comp_mean','seed']].head(16)

b.fill_bracket()
```

If you have any questions/issues/ideas for improvement, feel free to add them in the Issues. I hope you enjoy this project!

Finally, I'd like to say a major THANK YOU to everyone who develops and posts their college basketball ratings online for us to use!








