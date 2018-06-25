# jukola-xml-model
Analyze and estimate Jukola Relay results

## Setup
```bash
pipenv install
```

Fetch xml files (history) and running order for year to predict:

```bash
time for year in $(seq 2011 2017); do echo "YEAR $year"; time wget -P data http://results.jukola.com/tulokset/results_j${year}_ju.xml; done
time pipenv run python fetch_running_order.py && wc data/running_order_j2018_ju.tsv
```

Convert xml to csv and join years by runner name and team:

```bash
time for year in $(seq 2012 2017); do echo "YEAR $year"; time pipenv run python result_xml_to_csv.py $year && head data/csv-results_j${year}_ju.tsv; done
time pipenv run python group_csv.py && head data/grouped_paces_ju.tsv
```

Start jupyter:
```bash
pipenv run jupyter notebook
```

And navigate to `2018-lognormal-estimates` in browser.


## TODO

* Weighted means and stds
* Better estimate for unknown runners
* Proper split to train and test data sets
* Probability of mass start and need for head lamp
* Compare distributions. Is there something better than lognormal?