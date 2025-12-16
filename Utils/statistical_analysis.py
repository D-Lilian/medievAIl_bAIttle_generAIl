# -*- coding: utf-8 -*-
"""
@file statistical_analysis.py
@brief Statistical Analysis Module for Battle Simulations

@details
Provides comprehensive statistical analysis tools for battle data including:
- Descriptive statistics
- Hypothesis testing (t-tests, chi-square, ANOVA)
- Effect size calculations (Cohen's d, eta-squared)
- Confidence intervals
- Correlation analysis
- Distribution analysis

Designed for professional data analysis workflows.

"""

import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

import pandas as pd
import numpy as np
from scipy import stats

from Utils.battle_data import PlotData, AggregatedResults, BattleResult


@dataclass
class DescriptiveStats:
    """Descriptive statistics for a variable."""
    n: int
    mean: float
    std: float
    median: float
    min_val: float
    max_val: float
    q1: float
    q3: float
    iqr: float
    skewness: float
    kurtosis: float
    se: float  # Standard error
    ci_lower: float  # 95% CI lower
    ci_upper: float  # 95% CI upper
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'N': self.n,
            'Mean': self.mean,
            'Std': self.std,
            'SE': self.se,
            'Median': self.median,
            'Min': self.min_val,
            'Max': self.max_val,
            'Q1': self.q1,
            'Q3': self.q3,
            'IQR': self.iqr,
            'Skewness': self.skewness,
            'Kurtosis': self.kurtosis,
            '95% CI Lower': self.ci_lower,
            '95% CI Upper': self.ci_upper,
        }


@dataclass
class HypothesisTestResult:
    """Result of a hypothesis test."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    effect_size_name: Optional[str] = None
    interpretation: str = ""
    significant: bool = False
    alpha: float = 0.05
    
    def __post_init__(self):
        self.significant = self.p_value < self.alpha
        if not self.interpretation:
            self.interpretation = self._generate_interpretation()
    
    def _generate_interpretation(self) -> str:
        sig_text = "significant" if self.significant else "not significant"
        effect_text = ""
        if self.effect_size is not None:
            effect_text = f" Effect size ({self.effect_size_name}): {self.effect_size:.3f}"
            # Interpret effect size
            if self.effect_size_name == "Cohen's d":
                if abs(self.effect_size) < 0.2:
                    effect_text += " (negligible)"
                elif abs(self.effect_size) < 0.5:
                    effect_text += " (small)"
                elif abs(self.effect_size) < 0.8:
                    effect_text += " (medium)"
                else:
                    effect_text += " (large)"
        
        return f"Result is {sig_text} at α={self.alpha} (p={self.p_value:.4f}).{effect_text}"


class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis for battle simulation data.
    """
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize the analyzer.
        
        @param alpha: Significance level for hypothesis tests
        """
        self.alpha = alpha
    
    # =========================================================================
    # DESCRIPTIVE STATISTICS
    # =========================================================================
    
    def descriptive_stats(self, data: np.ndarray) -> DescriptiveStats:
        """
        Calculate comprehensive descriptive statistics.
        
        @param data: Array of values
        @return: DescriptiveStats object
        """
        data = np.array(data)
        data = data[~np.isnan(data)]  # Remove NaN
        
        n = len(data)
        if n == 0:
            return DescriptiveStats(
                n=0, mean=0, std=0, median=0, min_val=0, max_val=0,
                q1=0, q3=0, iqr=0, skewness=0, kurtosis=0,
                se=0, ci_lower=0, ci_upper=0
            )
        
        mean = np.mean(data)
        std = np.std(data, ddof=1) if n > 1 else 0
        se = std / np.sqrt(n) if n > 0 else 0
        
        # 95% Confidence Interval
        if n > 1:
            t_crit = stats.t.ppf(0.975, df=n-1)
            ci_lower = mean - t_crit * se
            ci_upper = mean + t_crit * se
        else:
            ci_lower = ci_upper = mean
        
        q1, median, q3 = np.percentile(data, [25, 50, 75])
        
        # Skewness and Kurtosis (with warnings suppressed for small n)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            skewness = stats.skew(data) if n > 2 else 0
            kurtosis = stats.kurtosis(data) if n > 3 else 0
        
        return DescriptiveStats(
            n=n,
            mean=mean,
            std=std,
            median=median,
            min_val=np.min(data),
            max_val=np.max(data),
            q1=q1,
            q3=q3,
            iqr=q3 - q1,
            skewness=skewness,
            kurtosis=kurtosis,
            se=se,
            ci_lower=ci_lower,
            ci_upper=ci_upper
        )
    
    # =========================================================================
    # HYPOTHESIS TESTS
    # =========================================================================
    
    def independent_t_test(self, group1: np.ndarray, group2: np.ndarray,
                           equal_var: bool = True) -> HypothesisTestResult:
        """
        Independent samples t-test.
        
        H0: μ1 = μ2 (no difference between groups)
        H1: μ1 ≠ μ2 (significant difference)
        
        @param group1: First group data
        @param group2: Second group data
        @param equal_var: Assume equal variances (use Welch's t-test if False)
        @return: HypothesisTestResult
        """
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=equal_var)
        
        # Cohen's d effect size
        pooled_std = np.sqrt(
            ((len(group1) - 1) * np.var(group1, ddof=1) + 
             (len(group2) - 1) * np.var(group2, ddof=1)) /
            (len(group1) + len(group2) - 2)
        )
        cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0
        
        test_name = "Independent t-test" if equal_var else "Welch's t-test"
        
        return HypothesisTestResult(
            test_name=test_name,
            statistic=t_stat,
            p_value=p_value,
            effect_size=cohens_d,
            effect_size_name="Cohen's d",
            alpha=self.alpha
        )
    
    def paired_t_test(self, before: np.ndarray, after: np.ndarray) -> HypothesisTestResult:
        """
        Paired samples t-test.
        
        @param before: Before treatment data
        @param after: After treatment data
        @return: HypothesisTestResult
        """
        t_stat, p_value = stats.ttest_rel(before, after)
        
        # Cohen's d for paired samples
        diff = np.array(after) - np.array(before)
        cohens_d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0
        
        return HypothesisTestResult(
            test_name="Paired t-test",
            statistic=t_stat,
            p_value=p_value,
            effect_size=cohens_d,
            effect_size_name="Cohen's d",
            alpha=self.alpha
        )
    
    def one_way_anova(self, *groups) -> HypothesisTestResult:
        """
        One-way ANOVA test.
        
        H0: All group means are equal
        H1: At least one group mean differs
        
        @param groups: Variable number of group arrays
        @return: HypothesisTestResult
        """
        f_stat, p_value = stats.f_oneway(*groups)
        
        # Eta-squared effect size
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)
        
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_total = sum((x - grand_mean)**2 for x in all_data)
        
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        return HypothesisTestResult(
            test_name="One-way ANOVA",
            statistic=f_stat,
            p_value=p_value,
            effect_size=eta_squared,
            effect_size_name="η²",
            alpha=self.alpha
        )
    
    def chi_square_test(self, observed: np.ndarray, 
                        expected: Optional[np.ndarray] = None) -> HypothesisTestResult:
        """
        Chi-square goodness of fit test.
        
        @param observed: Observed frequencies
        @param expected: Expected frequencies (uniform if None)
        @return: HypothesisTestResult
        """
        observed = np.array(observed)
        
        if expected is None:
            chi2, p_value = stats.chisquare(observed)
        else:
            chi2, p_value = stats.chisquare(observed, f_exp=expected)
        
        # Cramér's V effect size
        n = np.sum(observed)
        k = len(observed)
        cramers_v = np.sqrt(chi2 / (n * (k - 1))) if n * (k - 1) > 0 else 0
        
        return HypothesisTestResult(
            test_name="Chi-square test",
            statistic=chi2,
            p_value=p_value,
            effect_size=cramers_v,
            effect_size_name="Cramér's V",
            alpha=self.alpha
        )
    
    def chi_square_independence(self, contingency_table: np.ndarray) -> HypothesisTestResult:
        """
        Chi-square test of independence.
        
        @param contingency_table: 2D array of observed frequencies
        @return: HypothesisTestResult
        """
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Cramér's V
        n = np.sum(contingency_table)
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0
        
        return HypothesisTestResult(
            test_name="Chi-square independence test",
            statistic=chi2,
            p_value=p_value,
            effect_size=cramers_v,
            effect_size_name="Cramér's V",
            alpha=self.alpha
        )
    
    def mann_whitney_u(self, group1: np.ndarray, 
                       group2: np.ndarray) -> HypothesisTestResult:
        """
        Mann-Whitney U test (non-parametric alternative to t-test).
        
        @param group1: First group data
        @param group2: Second group data
        @return: HypothesisTestResult
        """
        u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        
        # Rank-biserial correlation as effect size
        n1, n2 = len(group1), len(group2)
        r = 1 - (2 * u_stat) / (n1 * n2)
        
        return HypothesisTestResult(
            test_name="Mann-Whitney U test",
            statistic=u_stat,
            p_value=p_value,
            effect_size=r,
            effect_size_name="rank-biserial r",
            alpha=self.alpha
        )
    
    def kruskal_wallis(self, *groups) -> HypothesisTestResult:
        """
        Kruskal-Wallis H test (non-parametric alternative to ANOVA).
        
        @param groups: Variable number of group arrays
        @return: HypothesisTestResult
        """
        h_stat, p_value = stats.kruskal(*groups)
        
        # Epsilon-squared effect size
        all_data = np.concatenate(groups)
        n = len(all_data)
        epsilon_sq = (h_stat - len(groups) + 1) / (n - len(groups))
        
        return HypothesisTestResult(
            test_name="Kruskal-Wallis H test",
            statistic=h_stat,
            p_value=p_value,
            effect_size=max(0, epsilon_sq),
            effect_size_name="ε²",
            alpha=self.alpha
        )
    
    def shapiro_wilk(self, data: np.ndarray) -> HypothesisTestResult:
        """
        Shapiro-Wilk test for normality.
        
        H0: Data is normally distributed
        H1: Data is not normally distributed
        
        @param data: Data array
        @return: HypothesisTestResult
        """
        # Shapiro-Wilk has a sample size limit
        data = np.array(data)[:5000]
        
        w_stat, p_value = stats.shapiro(data)
        
        result = HypothesisTestResult(
            test_name="Shapiro-Wilk normality test",
            statistic=w_stat,
            p_value=p_value,
            alpha=self.alpha
        )
        result.interpretation = (
            f"Data {'appears normally distributed' if not result.significant else 'deviates from normality'} "
            f"(W={w_stat:.4f}, p={p_value:.4f})"
        )
        return result
    
    def levene_test(self, *groups) -> HypothesisTestResult:
        """
        Levene's test for equality of variances.
        
        H0: All groups have equal variance
        H1: At least one group has different variance
        
        @param groups: Variable number of group arrays
        @return: HypothesisTestResult
        """
        w_stat, p_value = stats.levene(*groups)
        
        result = HypothesisTestResult(
            test_name="Levene's test (homogeneity of variance)",
            statistic=w_stat,
            p_value=p_value,
            alpha=self.alpha
        )
        result.interpretation = (
            f"Variances are {'equal' if not result.significant else 'unequal'} "
            f"across groups (W={w_stat:.4f}, p={p_value:.4f})"
        )
        return result
    
    # =========================================================================
    # CORRELATION ANALYSIS
    # =========================================================================
    
    def pearson_correlation(self, x: np.ndarray, 
                           y: np.ndarray) -> Tuple[float, float, str]:
        """
        Pearson correlation coefficient.
        
        @param x: First variable
        @param y: Second variable
        @return: (correlation, p-value, interpretation)
        """
        r, p_value = stats.pearsonr(x, y)
        
        # Interpret strength
        abs_r = abs(r)
        if abs_r < 0.1:
            strength = "negligible"
        elif abs_r < 0.3:
            strength = "weak"
        elif abs_r < 0.5:
            strength = "moderate"
        elif abs_r < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        direction = "positive" if r > 0 else "negative"
        
        interpretation = f"{strength} {direction} correlation (r={r:.3f}, p={p_value:.4f})"
        
        return r, p_value, interpretation
    
    def spearman_correlation(self, x: np.ndarray, 
                             y: np.ndarray) -> Tuple[float, float, str]:
        """
        Spearman rank correlation coefficient.
        
        @param x: First variable
        @param y: Second variable
        @return: (correlation, p-value, interpretation)
        """
        rho, p_value = stats.spearmanr(x, y)
        
        abs_rho = abs(rho)
        if abs_rho < 0.1:
            strength = "negligible"
        elif abs_rho < 0.3:
            strength = "weak"
        elif abs_rho < 0.5:
            strength = "moderate"
        elif abs_rho < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        direction = "positive" if rho > 0 else "negative"
        
        interpretation = f"{strength} {direction} monotonic relationship (ρ={rho:.3f}, p={p_value:.4f})"
        
        return rho, p_value, interpretation
    
    def correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix with p-values.
        
        @param df: DataFrame with numeric columns
        @return: DataFrame with correlations
        """
        cols = df.select_dtypes(include=[np.number]).columns
        n = len(cols)
        
        corr_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)
        p_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)
        
        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if i == j:
                    corr_matrix.loc[col1, col2] = 1.0
                    p_matrix.loc[col1, col2] = 0.0
                elif i < j:
                    r, p = stats.pearsonr(df[col1].dropna(), df[col2].dropna())
                    corr_matrix.loc[col1, col2] = r
                    corr_matrix.loc[col2, col1] = r
                    p_matrix.loc[col1, col2] = p
                    p_matrix.loc[col2, col1] = p
        
        return corr_matrix


class LanchesterAnalyzer:
    """
    Specialized analyzer for Lanchester's Laws hypothesis testing.
    
    Tests whether casualty data follows Linear Law (melee) or Square Law (ranged).
    """
    
    def __init__(self):
        self.stat_analyzer = StatisticalAnalyzer()
    
    def test_lanchester_law(self, data: Dict[str, PlotData]) -> Dict[str, Any]:
        """
        Test which Lanchester Law best fits the data for each unit type.
        
        Linear Law: casualties ∝ N (R² closer to 1 for linear fit)
        Square Law: casualties ∝ N² (R² closer to 1 for quadratic fit)
        
        @param data: Dictionary of PlotData per unit type
        @return: Analysis results
        """
        results = {}
        
        for unit_type, plot_data in data.items():
            if not plot_data.n_values or not plot_data.avg_team_b_casualties:
                continue
            
            n = np.array(plot_data.n_values)
            casualties = np.array(plot_data.avg_team_b_casualties)
            
            # Fit linear model: y = a*n + b
            try:
                slope_lin, intercept_lin, r_lin, p_lin, se_lin = stats.linregress(n, casualties)
                r2_linear = r_lin ** 2
            except Exception:
                r2_linear = 0
                slope_lin = p_lin = 0
            
            # Fit quadratic model: y = a*n² + b*n + c
            try:
                coeffs_quad = np.polyfit(n, casualties, 2)
                predicted_quad = np.polyval(coeffs_quad, n)
                ss_res = np.sum((casualties - predicted_quad) ** 2)
                ss_tot = np.sum((casualties - np.mean(casualties)) ** 2)
                r2_quadratic = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            except Exception:
                r2_quadratic = 0
                coeffs_quad = [0, 0, 0]
            
            # Fit square root model: y = a*sqrt(n) + b (alternative for ranged)
            try:
                sqrt_n = np.sqrt(n)
                slope_sqrt, intercept_sqrt, r_sqrt, p_sqrt, se_sqrt = stats.linregress(sqrt_n, casualties)
                r2_sqrt = r_sqrt ** 2
            except Exception:
                r2_sqrt = 0
            
            # Determine best fit
            fits = {
                'Linear': r2_linear,
                'Quadratic': r2_quadratic,
                'Square Root': r2_sqrt
            }
            best_fit = max(fits, key=fits.get)
            
            # Expected law based on unit type
            is_ranged = unit_type.lower() in ['crossbowman', 'crossbow', 'archer', 'ranged']
            expected_law = "Square Law (ranged)" if is_ranged else "Linear Law (melee)"
            
            # Actual law interpretation
            if best_fit == 'Linear':
                actual_law = "Linear Law"
                conclusion = "casualties scale linearly with N"
            elif best_fit == 'Quadratic':
                actual_law = "Square Law"
                conclusion = "casualties scale quadratically with N"
            else:
                actual_law = "Sub-linear"
                conclusion = "casualties scale sub-linearly (sqrt) with N"
            
            results[unit_type] = {
                'expected_law': expected_law,
                'actual_law': actual_law,
                'conclusion': conclusion,
                'r2_linear': r2_linear,
                'r2_quadratic': r2_quadratic,
                'r2_sqrt': r2_sqrt,
                'best_fit': best_fit,
                'best_r2': fits[best_fit],
                'linear_slope': slope_lin,
                'linear_p_value': p_lin,
                'matches_theory': (
                    (is_ranged and best_fit in ['Quadratic', 'Square Root']) or
                    (not is_ranged and best_fit == 'Linear')
                ),
                'n_observations': len(n),
            }
        
        return results
    
    def compare_unit_types(self, data: Dict[str, PlotData]) -> Dict[str, Any]:
        """
        Statistical comparison between unit types.
        
        @param data: Dictionary of PlotData per unit type
        @return: Comparison results
        """
        results = {}
        unit_types = list(data.keys())
        
        if len(unit_types) < 2:
            return {"error": "Need at least 2 unit types for comparison"}
        
        # Extract casualty data for each unit type
        casualties_by_type = {}
        for ut, plot_data in data.items():
            casualties_by_type[ut] = np.array(plot_data.avg_team_b_casualties)
        
        # Pairwise t-tests
        comparisons = []
        for i, type1 in enumerate(unit_types):
            for type2 in unit_types[i+1:]:
                if len(casualties_by_type[type1]) > 0 and len(casualties_by_type[type2]) > 0:
                    # Pad arrays to same length if needed
                    min_len = min(len(casualties_by_type[type1]), len(casualties_by_type[type2]))
                    
                    test_result = self.stat_analyzer.independent_t_test(
                        casualties_by_type[type1][:min_len],
                        casualties_by_type[type2][:min_len]
                    )
                    
                    comparisons.append({
                        'comparison': f"{type1} vs {type2}",
                        'type1_mean': np.mean(casualties_by_type[type1]),
                        'type2_mean': np.mean(casualties_by_type[type2]),
                        't_statistic': test_result.statistic,
                        'p_value': test_result.p_value,
                        'effect_size': test_result.effect_size,
                        'significant': test_result.significant,
                        'interpretation': test_result.interpretation
                    })
        
        results['pairwise_comparisons'] = comparisons
        
        # ANOVA if 3+ groups
        if len(unit_types) >= 3:
            groups = [casualties_by_type[ut] for ut in unit_types if len(casualties_by_type[ut]) > 0]
            if len(groups) >= 3:
                anova_result = self.stat_analyzer.one_way_anova(*groups)
                results['anova'] = {
                    'f_statistic': anova_result.statistic,
                    'p_value': anova_result.p_value,
                    'eta_squared': anova_result.effect_size,
                    'significant': anova_result.significant,
                    'interpretation': anova_result.interpretation
                }
        
        return results


def create_analysis_dataframe(data: Dict[str, PlotData]) -> pd.DataFrame:
    """
    Convert PlotData to a tidy DataFrame for analysis.
    
    @param data: Dictionary of PlotData per unit type
    @return: Tidy DataFrame
    """
    rows = []
    for unit_type, plot_data in data.items():
        for i, n in enumerate(plot_data.n_values):
            if i >= len(plot_data.avg_team_a_casualties):
                continue
            rows.append({
                'unit_type': unit_type,
                'n': n,
                'army_size_ratio': 2.0,  # 2N vs N
                'team_a_initial': n,
                'team_b_initial': 2 * n,
                'team_a_casualties': plot_data.avg_team_a_casualties[i],
                'team_b_casualties': plot_data.avg_team_b_casualties[i],
                'team_a_survivors': plot_data.avg_team_a_survivors[i] if i < len(plot_data.avg_team_a_survivors) else 0,
                'team_b_survivors': plot_data.avg_team_b_survivors[i] if i < len(plot_data.avg_team_b_survivors) else 0,
                'team_a_win_rate': plot_data.team_a_win_rates[i] if i < len(plot_data.team_a_win_rates) else 0,
                'team_b_win_rate': plot_data.team_b_win_rates[i] if i < len(plot_data.team_b_win_rates) else 0,
                'avg_duration': plot_data.avg_ticks[i] if i < len(plot_data.avg_ticks) else 0,
                # Derived metrics
                'team_a_casualty_rate': plot_data.avg_team_a_casualties[i] / n if n > 0 else 0,
                'team_b_casualty_rate': plot_data.avg_team_b_casualties[i] / (2 * n) if n > 0 else 0,
                'casualty_ratio': (plot_data.avg_team_b_casualties[i] / plot_data.avg_team_a_casualties[i] 
                                  if plot_data.avg_team_a_casualties[i] > 0 else 0),
            })
    
    return pd.DataFrame(rows)
