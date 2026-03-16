# Automated NCAA Bracket Selection with Python

A Python project that seeds an NCAA Basketball Tournament bracket using composite rankings and ratings data from [Massey Ratings](https://masseyratings.com/), then generates a PDF bracket. See [the original blog post](https://ryangooch.github.io/Automated-Selection-Committee/) for background on the approach.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

Install dependencies:

```bash
uv sync
```

### Dependencies

* [NumPy](http://www.numpy.org/)
* [pandas](http://pandas.pydata.org/)
* [openpyxl](https://openpyxl.readthedocs.io/en/default/)
* [Selenium](https://selenium-python.readthedocs.io/) (for scraping certain ratings sources)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
* [lxml](https://lxml.de/)
* [Requests](https://docs.python-requests.org/)
* [ReportLab](https://www.reportlab.com/) (PDF bracket generation)

## Usage

### CLI (recommended)

The quickest way to generate a bracket is with `main.py`:

```bash
# Generate a bracket PDF with default settings
uv run python main.py

# Specify output path and title
uv run python main.py -o brackets/my_bracket.pdf -t "My 2026 Bracket"

# Use raw ratings instead of rankings
uv run python main.py --use-metrics

# Exclude human polls
uv run python main.py --no-human-polls

# Choose specific computer polls
uv run python main.py --polls Sag Pom MAS

# Override conference auto-bid winners
uv run python main.py --conf-winner ACC=Duke SEC=Auburn

# Skip re-downloading the Massey CSV (use an existing file)
uv run python main.py --skip-download

# Also save an Excel bracket
uv run python main.py --excel
```

### Python API

You can also use the `Bracketeer` class directly:

```python
from metrics import Bracketeer

b = Bracketeer()

# Select the 68-team tournament field
b.get_tourney_teams()

# View the field
b.final_68

# Generate a PDF bracket
b.save_bracket_pdf()

# Or save to Excel
b.fill_bracket()
```

#### Customizing poll selection and ranking

```python
from metrics import Bracketeer

b = Bracketeer()

# View available polls
b.print_polls()

# Use a subset of computer polls and a custom ranking function
import numpy as np

comp_polls = ['POM', 'SAG', 'MAS']

def rank_calc(x, y):
    """Average polls, weighting computer over human 3-to-1."""
    if np.isnan(y):
        return x
    return (3 * x + y) / 4.0

b.get_tourney_teams(
    comp_polls=comp_polls,
    rank_calc_func=rank_calc,
)

b.final_68.head(16)
b.save_bracket_pdf()
```

#### Using ratings instead of rankings

The default mode uses *rankings* (ordinal positions) from the Massey composite. You can instead use *ratings* (the actual numerical values from each system), which can produce more nuanced results:

```python
from metrics import Bracketeer

b = Bracketeer()

comp_polls = ['POM', 'DOK', 'EBP']

b.get_tourney_teams(
    comp_polls=comp_polls,
    human_polls=False,
    use_metrics=True,
)

b.final_68[['Team', 'Conf', 'comp_mean', 'seed']].head(16)
b.save_bracket_pdf()
```

Currently supported ratings sources (via `scrape.py`):
* [KenPom](https://kenpom.com/)
* [ESPN BPI](http://www.espn.com/mens-college-basketball/bpi)
* [Dokter Entropy](http://www.timetravelsports.com/colbb.html)
* [Massey](https://www.masseyratings.com/cb/ncaa-d1/ratings)

## Project structure

| File / Dir | Description |
| --- | --- |
| `main.py` | CLI entry point |
| `metrics.py` | `Bracketeer` class — team selection, seeding, bracket logic |
| `bracket_pdf.py` | PDF bracket generation with ReportLab |
| `scrape.py` | Scrapers for individual ratings sources |
| `brackets/` | Generated bracket PDFs |
| `plots/` | Analysis plots |
| `notebooks/` | Jupyter notebooks for exploration |
| `csv_files/` | Cached CSV data |
| `bracket_template.xlsx` | Excel bracket template |

## Acknowledgments

A major thank you to everyone who develops and posts their college basketball ratings online, and to the projects that make this code possible.

If you have questions, ideas, or issues, feel free to open an Issue!
