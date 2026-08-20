# GitHub Machine-Learning Repository Analysis

## Project overview

This Level 3 Project 2 completes an end-to-end data analytics workflow using real repository records retrieved from the GitHub Search API. The project collects the 100 most-starred repositories returned for the query `machine learning`, prepares an analysis-ready CSV with Pandas, imports it into SQLite, answers the required questions with SQL, creates Matplotlib visualizations, interprets the results, and manages the work with Git and GitHub.

> **Data snapshot note:** GitHub repository metrics change over time. The CSV and database in this repository are a dated snapshot retrieved on 20 August 2026 UTC. Re-running the collection script will create a new snapshot and may produce different values.

## Repository contents

| File or folder | Purpose |
|---|---|
| `collect_data.py` | Retrieves the GitHub API response, explores and cleans the data, extracts nested values, handles missing values and duplicates, renames fields, saves `github_projects.csv`, and verifies the reload. |
| `analyze_data.py` | Creates the `Repositories` SQLite table, executes all required SQL queries, writes `sql_results.json`, creates the charts, and writes the interpretation. |
| `project_workflow.ipynb` | Single-notebook project workflow suitable for opening in Google Colab or Jupyter. |
| `github_projects.csv` | Cleaned 100-row dataset with the ten required analysis columns. |
| `github_projects.db` | SQLite database containing the `Repositories` table. |
| `github_api_response.json` | Raw API response retained for provenance and reproducibility. |
| `collection_summary.json` | Collection, cleaning, missing-value, duplicate, and reload-verification summary. |
| `sql_results.json` | Saved outputs from the required SQL queries. |
| `charts/top_10_repositories_by_stars.png` | Bar chart of the ten most-starred repositories. |
| `charts/repository_creation_trends.png` | Line chart of repository creation counts by month. |
| `analysis_findings.md` | Interpretation of the SQL outputs and charts. |
| `ethics_reflection.md` | Reflection on responsible use of public API data. |
| `evidence/` | Git and GitHub publication evidence. |

## Reproduce the project

Install the dependencies listed in `requirements.txt`, then run the scripts from the project directory:

```bash
python3 collect_data.py
python3 analyze_data.py
```

The collection script uses the required API URL and will use `GITHUB_TOKEN` or `GH_TOKEN` when available so that authenticated GitHub API requests avoid the public rate limit. It does not write credentials to any project file. The analysis script rebuilds the SQLite database from the cleaned CSV, executes every required query, and regenerates both charts.

## Main results from this snapshot

The dataset contains **100 repositories** with an average of **20,813.38 stars**. The top three repositories by stars are `tensorflow` with 197,103 stars, `transformers` with 164,278 stars, and `ML-For-Beginners` with 89,619 stars. The language grouping query found four languages with more than five repositories: Python, Unknown, Jupyter Notebook, and C++.

These results are descriptive, not a quality ranking. Stars, forks, watchers, issues, language labels, and creation dates are public indicators with limitations. They should be combined with additional checks such as recent commits, issue resolution, documentation quality, licensing review, and security assessment before business decisions are made.

## Rubric coverage

| Rubric area | Evidence in this repository |
|---|---|
| API collection and DataFrame exploration | `collect_data.py`, `github_api_response.json`, and `collection_summary.json` |
| Required columns and nested-value extraction | `collect_data.py` and the 10-column schema in `github_projects.csv` |
| Missing values and duplicates | Cleaning policy and counts in `collection_summary.json` |
| Date conversion and renamed fields | `github_projects.csv` and `collect_data.py` |
| CSV save and verification | Reload assertion in `collect_data.py` and `collection_summary.json` |
| SQLite database and `Repositories` table | `github_projects.db` and `sql_results.json` |
| Filtering, searching, logical operators, sorting, limiting, aggregates, grouping | `analyze_data.py` and `sql_results.json` |
| Matplotlib charts and interpretation | `charts/` and `analysis_findings.md` |
| Git initialization, staging, commits, and GitHub publication | `evidence/` and the repository history |
| Ethics reflection | `ethics_reflection.md` |

## Sources

[1] [GitHub REST API Search documentation](https://docs.github.com/en/rest/search/search)

[2] [Pandas documentation](https://pandas.pydata.org/docs/)

[3] [SQLite documentation](https://www.sqlite.org/docs.html)

[4] [Matplotlib documentation](https://matplotlib.org/stable/)
