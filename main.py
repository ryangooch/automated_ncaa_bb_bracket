#!/usr/bin/env python3
"""CLI to seed an NCAA tournament and produce a PDF bracket."""

import argparse
import sys

from metrics import Bracketeer


def parse_conf_winners(pairs):
    """Parse 'Conf=Team' pairs into a dict."""
    if not pairs:
        return None
    winners = {}
    for pair in pairs:
        if '=' not in pair:
            print(f"Error: conf-winner '{pair}' must be in Conf=Team format",
                  file=sys.stderr)
            sys.exit(1)
        conf, team = pair.split('=', 1)
        winners[conf] = team
    return winners


def main():
    parser = argparse.ArgumentParser(
        description='Generate an NCAA tournament bracket PDF.')

    parser.add_argument('-o', '--output', default=None,
                        help='Output PDF path (default: brackets/bracket_<date>.pdf)')
    parser.add_argument('-t', '--title', default=None,
                        help='Bracket title text')
    parser.add_argument('--polls', nargs='+', default=None,
                        help='Computer poll abbreviations to use (e.g. Sag Pom)')
    parser.add_argument('--use-metrics', action='store_true',
                        help='Use raw ratings data instead of rankings')
    parser.add_argument('--no-human-polls', action='store_true',
                        help='Exclude human polls (AP, USA) from ranking')
    parser.add_argument('--conf-winner', nargs='+', default=None,
                        metavar='CONF=TEAM',
                        help='Override conference auto-bid winners (e.g. ACC=Duke)')
    parser.add_argument('--csv', default='masseyratings.csv',
                        help='Path for the Massey Ratings CSV (default: masseyratings.csv)')
    parser.add_argument('--skip-download', action='store_true',
                        help='Skip downloading CSV; use existing file at --csv path')
    parser.add_argument('--excel', action='store_true',
                        help='Also save an Excel bracket file')

    args = parser.parse_args()

    conf_winners = parse_conf_winners(args.conf_winner)

    if args.skip_download:
        print('Using existing CSV file...')
    else:
        print('Initializing bracket (downloading latest Massey Ratings)...')
    bracket = Bracketeer(csv_save_path=args.csv, skip_download=args.skip_download)

    print('Selecting tournament field and seeding teams...')
    bracket.get_tourney_teams(
        comp_polls=args.polls,
        conf_winners=conf_winners,
        use_metrics=args.use_metrics,
        human_polls=not args.no_human_polls,
    )

    pdf_path = bracket.save_bracket_pdf(output_path=args.output, title=args.title)
    print(f'Bracket PDF saved to: {pdf_path}')

    if args.excel:
        bracket.fill_bracket()
        print('Excel bracket saved.')


if __name__ == '__main__':
    main()
