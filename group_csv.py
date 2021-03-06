import collections
import csv
import logging
import sys
from collections import defaultdict

import numpy as np

# time pipenv run python group_csv.py ve && head data/grouped_paces_ve.tsv

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

ve_or_ju = sys.argv[1]

years = {
    "ve": ["2018", "2017", "2016", "2015", "2014", "2013", "2012"],
    "ju": ["2018", "2017", "2016", "2015", "2014", "2013", "2012"]
}

# time for year in $(seq 2011 2017); do echo "$year: [$(curl http://results.jukola.com/tulokset/fi/j${year}_ju/ | grep "<td><a href='/tulokset/fi/" | grep -E "Vaihto |Maali "| cut -d " " -f 3| tr ',' '.' | tr '\n' ',')]," >> years.txt; done

distances = {
    "ve": {
        2011: [6.9, 6.2, 5.1, 8.5],
        2012: [5.7, 5.8, 7.2, 8.4],
        2013: [8.2, 6.2, 6.2, 8.7],
        2014: [5.1, 5.0, 6.7, 7.4],
        2015: [8.0, 6.0, 6.2, 8.8],
        2016: [7.1, 6.7, 6.0, 9.1],
        2017: [6.7, 6.6, 5.7, 8.0],
        2018: [6.2, 6.2, 5.4, 7.9],
        2019: [6.0, 5.7, 7.3, 7.9]
    },
    "ju": {
        2011: [11.5, 11.4, 13.6, 8.3, 8.5, 10.5, 15.6],
        2012: [12.7, 12.7, 14.1, 7.7, 8.1, 10.2, 15.1],
        2013: [12.2, 13.0, 14.4, 7.8, 7.7, 11.7, 15.1],
        2014: [10.1, 11.5, 10.2, 7.6, 7.7, 10.7, 14.0],
        2015: [13.8, 12.3, 15.8, 8.1, 8.6, 12.6, 14.6],
        2016: [10.7, 12.8, 14.1, 8.6, 8.7, 12.4, 16.5],
        2017: [12.8, 14.3, 12.3, 7.7, 7.8, 11.1, 13.8],
        2018: [11.0, 11.9, 12.7, 8.8, 8.7, 10.8, 15.1],
        2019: [10.9, 10.5, 13.2, 7.3, 7.8, 11.1, 12.9]
    }
}

by_name = {}


def read_team_countries(year, ve_or_ju):
    with open(f'data/running_order_j{year}_{ve_or_ju}.tsv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        next(csvreader, None)  # skip the headers
        country_by_team_id = {}
        for row in csvreader:
            team_id = int(row[0])
            team_country = row[3].upper()
            country_by_team_id[team_id] = team_country

        return country_by_team_id


for year in years[ve_or_ju]:
    country_by_team_id = read_team_countries(year, ve_or_ju)

    in_file_name = f'data/results_with_dist_j{year}_{ve_or_ju}.tsv'
    with open(in_file_name) as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        next(csvreader, None)  # skip the headers
        for row in csvreader:
            team_id = int(row[0])
            team_base_name = row[3].upper()
            name = row[8].lower()
            leg_nro = int(row[5])
            leg_time_str = row[7]

            if leg_time_str == "NA":
                leg_pace = "NA"
            else:
                leg_distance = distances[ve_or_ju][int(year)][leg_nro - 1]
                leg_pace = round((int(leg_time_str) / 60) / leg_distance, 3)

            if not name in by_name:
                by_name[name] = []

            run = {}
            run["name"] = name
            run["team_id"] = team_id
            run["team"] = team_base_name
            run["team_country"] = "NA"
            if team_id in country_by_team_id:
                run["team_country"] = country_by_team_id[team_id]
            run["year"] = year
            run["pace"] = leg_pace
            run["leg_nro"] = leg_nro
            by_name[name].append(run)
        csvfile.close()


def open_output_file(out_file_name, column_names):
    out_file = open(out_file_name, 'w')
    csvwriter = csv.writer(out_file, delimiter="\t", quoting=csv.QUOTE_ALL)
    csvwriter.writerow(column_names)
    return (out_file, csvwriter)


by_unique_name = {}
for name, runs in by_name.items():
    run_years = list(map(lambda run: run["year"], runs))
    unique_years = set(run_years)

    if len(run_years) == len(unique_years):
        by_unique_name[name] = runs
    else:
        by_team = defaultdict(list)
        for run in runs:
            team_name = run["team"]
            by_team[team_name].append(run)
        for team_name, runs_in_team in by_team.items():
            unique_name = name + ":" + team_name
            by_unique_name[unique_name] = runs_in_team

column_names = ["mean_team_id", "teams", "name", "num_runs", "num_valid_times", "mean_pace", "stdev", "most_common_leg",
                "most_common_country", "pace_1", "pace_2",
                "pace_3", "pace_4", "pace_5", "pace_6", "pace_7"]
(out_file, csvwriter) = open_output_file(f'data/grouped_paces_{ve_or_ju}.tsv', column_names)

for unique_name, runs in by_unique_name.items():
    team_ids = map(lambda run: run["team_id"], runs)
    teams = map(lambda run: run["team"], runs)
    joined_teams = ";".join(set(teams))
    paces = map(lambda run: run["pace"], runs)

    valid_paces = [pace for pace in paces if pace != "NA"]
    available_paces = valid_paces[:7] + ["NA" for x in range(7 - len(valid_paces))]

    median_team_id = round(np.median(list(team_ids)), 1)

    if len(valid_paces) > 7:
        print(unique_name)
        print(len(runs))
        for run in runs:
            print(run)

    if len(valid_paces) > 0:
        float_paces = np.array(valid_paces).astype(np.float)
        mean_pace = round(np.average(float_paces), 3)
        stdev = round(np.std(float_paces), 3)
        legs = map(lambda run: run["leg_nro"], runs)
        most_common_leg = collections.Counter(legs).most_common()[0][0]
        countries = map(lambda run: run["team_country"], runs)
        most_common_country = collections.Counter(countries).most_common()[0][0]
    else:
        mean_pace = "NA"
        stdev = "NA"

    row = [median_team_id, joined_teams, unique_name, len(runs), len(valid_paces), mean_pace, stdev, most_common_leg,
           most_common_country] + available_paces
    csvwriter.writerow(row)

out_file.close()

runs_file_cols = ["name", "year", "team_id", "team", "team_country", "pace", "leg_nro", "num_runs"]
(runs_out_file, runs_csvwriter) = open_output_file(f'data/runs_{ve_or_ju}.tsv', runs_file_cols)

for unique_name, runs in by_unique_name.items():
    for run in runs:
        pace = run["pace"]
        if pace != "NA":
            row = [unique_name, run["year"], run["team_id"], run["team"], run["team_country"], pace, run["leg_nro"],
                   len(runs)]
            runs_csvwriter.writerow(row)

runs_out_file.close()
