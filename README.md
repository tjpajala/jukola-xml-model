# jukola-xml-model
Analyze and estimate Jukola Relay results

## Setup
```bash
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
pipenv sync
```

Fetch xml files (history) and running orders:

```bash
time for year in $(seq 1992 2018); do echo "YEAR $year"; time wget -P data https://results.jukola.com/tulokset/results_j${year}_ju.xml; done
time for year in $(seq 2012 2018); do echo "YEAR $year"; time pipenv run python fetch_running_order.py ${year} && wc data/running_order_j${year}_ju.tsv; done

```

Convert xml to csv and join years by runner name and team:

```bash
time for year in $(seq 2012 2018); do echo "YEAR $year"; time pipenv run python result_xml_to_csv.py $year ve && head data/results_with_dist_j${year}_ve.tsv; done
time pipenv run python group_csv.py ve && head data/grouped_paces_ve.tsv
```

Start jupyter:
```bash
nice pipenv run jupyter notebook
```

And navigate to `2018-lognormal-estimates` in browser.


## TODO

* Weighted means and stds
* Better estimate for unknown runners
* Proper split to train and test data sets
* Probability of mass start and need for head lamp
* Compare distributions. Is there something better than lognormal?
