# Ethics Reflection: Responsible Use of Public API Data

## Why is it important to verify data collected from public APIs?

Verification is important because a successful HTTP response does not guarantee that every field is present, current, correctly typed, or appropriate for the intended analysis. API schemas can change, values can be null, and records can be duplicated or returned in an unexpected order. In this project, verification included checking the response structure, confirming that all required fields existed, inspecting the DataFrame shape and data types, extracting nested owner and license values, counting missing values, removing duplicate repositories, parsing dates, and reloading the saved CSV to confirm its schema and completeness. These checks reduce the risk of producing conclusions from malformed or incomplete records.

## Why should data analysts document the source of their data?

Documentation makes an analysis traceable and reproducible. A reader should be able to identify the exact API endpoint, query parameters, collection date, transformation rules, and saved artifacts used to produce the results. This project records the source URL in `collection_summary.json`, retains the raw API response, records the retrieval timestamp, and explains the cleaning policy. Documentation also communicates the limits of the dataset: this is a ranked API snapshot rather than a complete census of all machine-learning repositories, and GitHub metrics can change after collection.

## How can missing or inaccurate data affect analysis and decision-making?

Missing or inaccurate values can distort counts, averages, rankings, language comparisons, and trend charts. For example, treating a missing programming language as a real language could understate the size of other groups, while treating a missing license as an approved license could create legal and operational risk. Inaccurate dates could place repositories in the wrong time period, and duplicated records could inflate repository counts or summary statistics. The project uses explicit replacements for missing categorical and numeric values, removes duplicate owner-name records, removes rows with invalid dates, and reports the before-and-after quality checks. These steps improve reliability, but they do not eliminate all bias or uncertainty. Analysts should still validate important findings with additional sources and avoid interpreting popularity metrics as direct measures of quality, safety, or suitability.

## Responsible-use conclusion

Public availability does not remove the responsibility to use data carefully. Repository owners may reasonably expect public metadata to be analyzed in context, without misrepresenting project quality or making unsupported claims about individuals and organizations. A responsible analyst should preserve provenance, minimize unnecessary personal information, respect licenses, state the snapshot date, disclose limitations, and use the results as an input to human review rather than as an automatic decision.

## References

[1] [GitHub REST API Search documentation](https://docs.github.com/en/rest/search/search)

[2] [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
