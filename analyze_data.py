"""Load the cleaned repository data into SQLite, run rubric queries, and create charts."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "github_projects.csv"
DB_PATH = PROJECT_DIR / "github_projects.db"
RESULTS_PATH = PROJECT_DIR / "sql_results.json"
CHARTS_DIR = PROJECT_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)


def load_database() -> None:
    """Create Repositories and import the prepared CSV."""
    df = pd.read_csv(CSV_PATH)
    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql("Repositories", connection, if_exists="replace", index=False)
        row_count = connection.execute("SELECT COUNT(*) FROM Repositories").fetchone()[0]
    if row_count != len(df):
        raise AssertionError("SQLite row count does not match the cleaned CSV.")


def run_queries() -> dict[str, object]:
    """Execute all required SQL tasks and return JSON-serializable results."""
    with sqlite3.connect(DB_PATH) as connection:
        queries = {
            "more_than_10000_stars": """
                SELECT name, owner, stars, language
                FROM Repositories
                WHERE stars > 10000
                ORDER BY stars DESC
            """,
            "names_containing_machine": """
                SELECT name, owner, stars, language
                FROM Repositories
                WHERE name LIKE '%Machine%'
                   OR name LIKE '%machine%'
                ORDER BY stars DESC
            """,
            # Logical-operator query 1: AND.
            "logical_and": """
                SELECT name, owner, stars, language
                FROM Repositories
                WHERE stars > 10000 AND forks > 1000
                ORDER BY stars DESC
            """,
            # Logical-operator query 2: OR and NOT.
            "logical_or_not": """
                SELECT name, owner, stars, language
                FROM Repositories
                WHERE (language = 'Python' OR language = 'C++')
                  AND NOT license = 'No license'
                ORDER BY stars DESC
            """,
            # A second mixed logical query makes the AND/OR/NOT requirement explicit.
            "logical_mixed": """
                SELECT name, owner, stars, language
                FROM Repositories
                WHERE (stars > 10000 OR forks > 5000)
                  AND NOT name LIKE 'test%'
                ORDER BY stars DESC
            """,
            "top_10_by_stars": """
                SELECT name, owner, stars, forks, language
                FROM Repositories
                ORDER BY stars DESC
                LIMIT 10
            """,
            "total_repository_count": """
                SELECT COUNT(*) AS total_repositories
                FROM Repositories
            """,
            "average_stars": """
                SELECT ROUND(AVG(stars), 2) AS average_stars
                FROM Repositories
            """,
            "language_groups_more_than_5": """
                SELECT language, COUNT(*) AS repository_count,
                       ROUND(AVG(stars), 2) AS average_stars
                FROM Repositories
                GROUP BY language
                HAVING COUNT(*) > 5
                ORDER BY repository_count DESC, language
            """,
            "monthly_creation_trends": """
                SELECT substr(created_date, 1, 7) AS creation_month,
                       COUNT(*) AS repository_count
                FROM Repositories
                GROUP BY creation_month
                ORDER BY creation_month
            """,
        }
        results: dict[str, object] = {}
        for name, query in queries.items():
            frame = pd.read_sql_query(query, connection)
            results[name] = frame.to_dict(orient="records")

        table_info = connection.execute("PRAGMA table_info(Repositories)").fetchall()
        results["database_verification"] = {
            "database": DB_PATH.name,
            "table": "Repositories",
            "row_count": int(connection.execute("SELECT COUNT(*) FROM Repositories").fetchone()[0]),
            "columns": [row[1] for row in table_info],
        }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def create_visualizations(results: dict[str, object]) -> None:
    """Create the two required Matplotlib charts from SQL outputs."""
    plt.style.use("seaborn-v0_8-whitegrid")

    top10 = pd.DataFrame(results["top_10_by_stars"])
    top10 = top10.sort_values("stars", ascending=True)
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(top10["name"], top10["stars"], color="#2563eb")
    ax.set_title("Top 10 Machine-Learning Repositories by GitHub Stars", fontsize=15, weight="bold")
    ax.set_xlabel("Stars")
    ax.set_ylabel("Repository")
    ax.ticklabel_format(axis="x", style="plain")
    for index, value in enumerate(top10["stars"]):
        ax.text(value, index, f" {value:,.0f}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "top_10_repositories_by_stars.png", dpi=180)
    plt.close(fig)

    trends = pd.DataFrame(results["monthly_creation_trends"])
    trends["creation_month"] = pd.to_datetime(trends["creation_month"], format="%Y-%m")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(trends["creation_month"], trends["repository_count"], marker="o", color="#059669", linewidth=2)
    ax.set_title("Machine-Learning Repository Creation Trends", fontsize=15, weight="bold")
    ax.set_xlabel("Creation month")
    ax.set_ylabel("Number of repositories")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "repository_creation_trends.png", dpi=180)
    plt.close(fig)


def write_interpretation(results: dict[str, object]) -> None:
    """Write concise, data-supported findings for the project report."""
    top10 = pd.DataFrame(results["top_10_by_stars"])
    languages = pd.DataFrame(results["language_groups_more_than_5"])
    trends = pd.DataFrame(results["monthly_creation_trends"])
    total = results["total_repository_count"][0]["total_repositories"]
    average = results["average_stars"][0]["average_stars"]
    top_repo = top10.iloc[0]
    peak_month = trends.loc[trends["repository_count"].idxmax()]
    language_sentence = ", ".join(
        f"{row.language} ({int(row.repository_count)})" for row in languages.itertuples()
    )

    text = f"""# Analysis Findings

The cleaned dataset contains **{total} repositories**, and the mean repository popularity is **{average:,.2f} stars**. The most-starred repository in the top-ten result is **{top_repo['name']}**, with **{int(top_repo['stars']):,} stars**. The top-ten chart shows that popularity is concentrated among a small set of highly visible projects rather than distributed evenly across all 100 records.

The language grouping query retained languages with more than five repositories. The qualifying groups are **{language_sentence}**. This indicates that the sample is not language-neutral: a small number of languages account for most of the repositories, which is useful when considering skills, tooling, or documentation priorities.

The creation-trend query identifies **{peak_month['creation_month']}** as the month with the largest number of repositories in the sample, at **{int(peak_month['repository_count'])} repositories**. The line chart should be read as the distribution of creation dates within this API snapshot, not as a complete history of all machine-learning repositories on GitHub.

These findings support a practical business interpretation: star counts can help identify high-visibility projects for further review, while language and creation-date patterns can inform technical ecosystem monitoring. They should not be treated as measures of software quality, security, maintenance quality, or adoption without additional validation.
"""
    (PROJECT_DIR / "analysis_findings.md").write_text(text, encoding="utf-8")


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Run collect_data.py first: {CSV_PATH}")
    load_database()
    results = run_queries()
    create_visualizations(results)
    write_interpretation(results)
    print("SQLite database created:", DB_PATH)
    print("SQL results written:", RESULTS_PATH)
    print("Charts written:", sorted(path.name for path in CHARTS_DIR.glob("*.png")))
    print("Total repositories:", results["total_repository_count"])
    print("Average stars:", results["average_stars"])
    print("Top 10:\n", pd.DataFrame(results["top_10_by_stars"]).to_string(index=False))
    print("Languages with more than 5 repositories:\n", pd.DataFrame(results["language_groups_more_than_5"]).to_string(index=False))


if __name__ == "__main__":
    main()


# References:
# SQLite documentation: https://www.sqlite.org/docs.html
# Matplotlib documentation: https://matplotlib.org/stable/
