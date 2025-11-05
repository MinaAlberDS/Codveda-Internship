# Import needed libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sms
import warnings
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Literal
from sklearn.model_selection import train_test_split
from statsmodels.stats.multitest import multipletests

def set_xy(data, y_col, outliers=False, outliers_list=None, drop_cols=None):
    """
    Splits data into X (predictors) and y (target), with optional outlier filtering.
    
    Args:
        data (DataFrame): The input dataset.
        y_col (str): The name of the target variable column.
        outliers (bool, optional): If True, keep only outliers; if False, remove outliers. Defaults to False.
        outliers_list (list, optional): List of columns indicating outliers. Defaults to None.
        drop_cols (list, optional): Additional columns to drop from X. Defaults to None.
    """
    drop_cols = drop_cols + [y_col] or ["name", "log(price)", "log(price/sqm)", "Is log(price/sqm) outlier"]

    try:
        if outliers_list is not None:
            outliers_mask = data[outliers_list].max(axis=1)

            if outliers:
                data = data[outliers_mask]
            else:
                data = data[~outliers_mask]

            data = data.drop(outliers_list, axis=1)
    except Exception as e:
        print(f"Warning: outlier filtering skipped due to: {e}")

    x = data.drop(drop_cols, axis=1, errors='ignore')
    y = data[y_col]

    return [x, y]


def split_data(X,y, test_size:float = 0.2):
    """Split the data into train, and test data

    Args:
        X (DataFrame): X matrix
        y (array_like): The dependent variable
        test_size (float, optional): The percentage of test rows of the data. Defaults to 0.2.

    Returns:
        X_train, X_test, y_train, y_test: Return the train, and test data
    """
    # Split into train, and test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42) # test data is 20% of the data
    return [X_train, X_test, y_train, y_test]

def general_to_specific(df, y_col, x_cols, pval_threshold=0.05, vif_threshold=10.0,
                        correction='fdr_bh', verbose=True, robust_se:bool=False, reg_type: Literal["Logistic", "Linear"] = "Linear"):
    """
    General-to-Specific model selection using corrected p-values and VIF reduction.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing dependent and independent variables.
    y_col : str
        Dependent variable name.
    x_cols : list
        Initial list of independent variable names.
    pval_threshold : float
        Threshold for corrected p-values (default = 0.05).
    vif_threshold : float
        Threshold for Variance Inflation Factor (default = 10).
    correction : str
        Type of p-value correction ('bonferroni', 'fdr_bh', etc.).
    verbose : bool
        Whether to print progress.
    robust_se : bool
        Whether to use robust standard errors (only for Linear regression).
    reg_type ("Logistic", "Linear"): Select the regression to perform the GETS method

    Returns
    -------
    model :
        Final model.
    removed_vars : list
        Variables removed during the selection process.
    Final_vifs: list
        the final vifs values
    """
    removed_vars = []
    current_x = x_cols.copy()

    while True:
        X = sms.add_constant(df[current_x])
        y = df[y_col]
        if reg_type == "Linear":
            if robust_se:
                model = sms.OLS(y, X).fit(cov_type='HC3') # robust standard error for t-tests
            else:
                model = sms.OLS(y, X).fit() # robust standard error for t-tests
        elif reg_type == "Logistic":
            model = sms.Logit(y,X).fit()

        # 1️⃣ Corrected p-values
        pvals = model.pvalues.drop('const', errors='ignore')
        _, corrected_pvals, _, _ = multipletests(pvals, method=correction)
        corrected = pd.Series(corrected_pvals, index=pvals.index)

        worst_p = corrected.max()
        worst_var_p = corrected.idxmax()

        # 2️⃣ VIF calculation
        vif_df = pd.DataFrame({
            'Variable': current_x,
            'VIF': [variance_inflation_factor(X.values, i+1) for i in range(len(current_x))]
        })
        worst_vif = vif_df['VIF'].max()
        try: # To avoid infinity floats
            worst_vif_int = int(worst_vif)
        except: worst_vif_int = worst_vif
        worst_var_vif = vif_df.loc[vif_df['VIF'].idxmax(), 'Variable']

        # 3️⃣ Decide what to remove
        if worst_p > pval_threshold or worst_vif_int > vif_threshold:
            if worst_p > pval_threshold:
                worst_var = worst_var_p
                reason = f"corrected p={worst_p:.4f}"
            elif worst_vif > vif_threshold:
                worst_var = worst_var_vif
                reason = f"VIF {worst_vif:.2f}"
            else:
                break  # Should not happen, but handle the case

            if verbose:
                print(f"Removing {worst_var} due to {reason}")
            current_x = [v for v in current_x if v != worst_var]
            removed_vars.append(worst_var)
        else:
            if verbose:
                print("No variable exceeds corrected p-value or VIF threshold. Selection complete.")
                break

    # Final VIFs for sanity check
    final_X = sms.add_constant(df[current_x])
    final_vif = pd.DataFrame({
        'Variable': current_x,
        'VIF': [variance_inflation_factor(final_X.values, i+1) for i in range(len(current_x))]
    })

    if verbose:
        print("\nFinal VIFs:")
        print(final_vif.sort_values('VIF', ascending=False).to_string(index=False))
        print(f"The final model summary:\n{model.summary2()}")
    return model, removed_vars, final_vif

def reg_summary(X_train, y_train, reg_type: Literal["Logistic", "Linear"] = "Linear"):
    """Return the statsmodels model summary

    Args:
        X_train (DataFrame): X train matrix
        y_train (Array_like): Dependent variable
        reg_type ("Logistic", "Linear"): Select the regression to perform the summary
    Returns:
        Model_summary: Return the model summary(F-statistic, R-squared, etc.)
    """
### See the summary of the model using statsmodels

    if reg_type == "Logistic":
        reg_sms = sms.Logit(y_train, sms.add_constant(X_train)).fit()
    elif reg_type == "Linear":
        reg_sms = sms.OLS(y_train, sms.add_constant(X_train)).fit()

    results = reg_sms.summary2()

    print(f"The regression model summary:\n{results}")