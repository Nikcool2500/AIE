from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


def test_high_cardinality_detection():
    many_categories = [f"category_{i}" for i in range(100)]
    df = pd.DataFrame({
        "user_id": range(100),
        "high_card_col": many_categories
    })
    
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df, df)
    
    assert flags.get("has_high_cardinality", False) == True


def test_duplicate_id_detection():
    df = pd.DataFrame({
        "user_id": [1, 2, 2, 3, 4, 4],
        "value": [10, 20, 30, 40, 50, 60],
    })
    
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df, df)
    
    assert flags.get("duplicates", False) == True


def test_quality_score_calculation():
    good_df = pd.DataFrame({
        "id": [i for i in range(101)],
        "value": [i * 10 for i in range(101)],
        "category": (['1', '2', '3'] * 34)[:101]
    })
    
    bad_df = pd.DataFrame({
        "id": [i // 2 for i in range(1, 102)],
        "high_card": [f"val_{i}" for i in range(101)]
    })
    
    good_summary = summarize_dataset(good_df)
    good_missing = missing_table(good_df)
    good_flags = compute_quality_flags(good_summary, good_missing, good_df)
    
    bad_summary = summarize_dataset(bad_df)
    bad_missing = missing_table(bad_df)
    bad_flags = compute_quality_flags(bad_summary, bad_missing, bad_df)
    
    assert good_flags["quality_score"] > bad_flags["quality_score"]
    assert good_flags["quality_score"] >= 0.9
    assert bad_flags["quality_score"] <= 0.7
