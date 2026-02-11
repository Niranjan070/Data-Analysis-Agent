# 🎬 Demo & Sample Outputs

## Sample Analysis Results

### Dataset: Titanic Sample (891 rows × 10 columns)

---

### Schema Compression Results

```
Compression Ratio: 189.8x
Full Schema Tokens: 21,450
Compressed Tokens: 113
Savings: 99.5%
```

#### Compressed Schema Output:
```
DS:Titanic Sample|891r×10c|0.19MB
COLS:
  PassengerId(i64)|uniq:891|[1..891]|μ=446.00
  Survived(i64)|uniq:2|[0..1]|μ=0.38|⚠cat
  Pclass(i64)|uniq:3|[1..3]|μ=2.31|⚠cat
  Name(str)|uniq:891|top:Passenger_0,Passenger_1,Passenger_2
  Sex(str)|uniq:2|top:male,female
  Age(f64)|null:19.8%|uniq:88|[1.0..80.0]|μ=29.70
  SibSp(i64)|uniq:6|[0..5]|μ=0.42|⚠cat|skew:high_right
  Parch(i64)|uniq:5|[0..4]|μ=0.37|⚠cat|skew:high_right
  Fare(f64)|uniq:823|[0.01..234.50]|μ=32.10|skew:high_right
  Embarked(str)|null:2.0%|uniq:3|top:S,C,Q
```

---

### Overview Tool Output

```
==================================================
DATASET OVERVIEW
==================================================
Shape: 891 rows × 10 columns
Memory Usage: 0.19 MB

Column Types:
int64     5
object    3
float64   2

Null Summary:
                      Nulls   Pct
Age                    177  19.9
Embarked                18   2.0

First 5 rows:
   PassengerId  Survived  Pclass        Name     Sex   Age  SibSp  Parch   Fare Embarked
0            1         0       3  Passenger_0    male  44.2      0      0  53.39        S
1            2         0       2  Passenger_1  female  38.4      0      0  23.17        S
...
```

---

### Correlation Analysis Output

```
==================================================
CORRELATION ANALYSIS
==================================================

Top Correlations (|r| > 0.3):
  🟢 Pclass ↔ Fare: -0.347
  🟢 SibSp ↔ Parch: +0.315
```

Generated Chart: Correlation heatmap with dark theme styling.

---

### Distribution Analysis Output

```
==================================================
DISTRIBUTION ANALYSIS
==================================================
  PassengerId: skew=0.00, kurtosis=-1.20
  Survived: skew=0.49, kurtosis=-1.76
  Pclass: skew=-0.59, kurtosis=-1.24
  Age: skew=0.37, kurtosis=-0.53
  SibSp: skew=3.62, kurtosis=16.88 ⚠ highly skewed ⚠ heavy tails
  Parch: skew=3.13, kurtosis=11.95 ⚠ highly skewed ⚠ heavy tails
  Fare: skew=2.12, kurtosis=5.93 ⚠ highly skewed
```

Generated Chart: Histograms with KDE overlay for each numeric column.

---

### Missing Value Analysis Output

```
==================================================
MISSING VALUE ANALYSIS
==================================================
Total missing: 195/8910 (2.2%)

  Age                            ████░░░░░░░░░░░░░░░░  19.9% (177)
  Embarked                       █░░░░░░░░░░░░░░░░░░░   2.0% (18)
```

---

### Outlier Detection Output

```
==================================================
OUTLIER ANALYSIS (IQR Method)
==================================================
  PassengerId: 0 outliers (0.0%) | bounds: [-444.50, 1336.50]
  Survived: 0 outliers (0.0%) | bounds: [-1.50, 1.50]
  Pclass: 0 outliers (0.0%) | bounds: [-2.00, 6.00]
  Age: 3 outliers (0.3%) | bounds: [-5.25, 63.85]
  SibSp: 31 outliers (3.5%) | bounds: [-1.50, 1.50]
  Parch: 43 outliers (4.8%) | bounds: [-1.00, 1.00]
  Fare: 99 outliers (11.1%) | bounds: [-32.47, 67.51]

4/7 columns have outliers
```

---

## Token Savings Summary (After Full Auto-EDA)

```
┌─────────────────────┬────────────┐
│ Schema Compression  │    99.5%   │
│ History Compression │    76.0%   │
│ Total Tokens Saved  │   ~21,500  │
│ Analysis Steps      │      7     │
└─────────────────────┴────────────┘
```

---

## Compressed LLM Context

This is the full compressed context that would be sent to an LLM after Auto-EDA:

```
DATASET SCHEMA:
DS:Titanic Sample|891r×10c|0.19MB
COLS:
  PassengerId(i64)|uniq:891|[1..891]|μ=446.00
  Survived(i64)|uniq:2|[0..1]|μ=0.38|⚠cat
  Pclass(i64)|uniq:3|[1..3]|μ=2.31|⚠cat
  Name(str)|uniq:891|top:Passenger_0,...
  Sex(str)|uniq:2|top:male,female
  Age(f64)|null:19.8%|uniq:88|[1.0..80.0]|μ=29.70
  SibSp(i64)|uniq:6|[0..5]|μ=0.42|⚠cat
  Parch(i64)|uniq:5|[0..4]|μ=0.37|⚠cat
  Fare(f64)|uniq:823|[0.01..234.5]|μ=32.10|skew:high_right
  Embarked(str)|null:2%|uniq:3|top:S,C,Q

KEY FINDINGS:
  1. ⚠ SibSp: highly skewed ⚠ heavy tails
  2. ⚠ Parch: highly skewed ⚠ heavy tails
  3. ⚠ Fare: highly skewed
  4. 4/7 cols have outliers

LATEST STEPS:
  • [overview] Shape, types, memory usage
  • [describe] Statistical summary
  • [distributions] Histograms + skewness
  • [correlations] Heatmap + top pairs
  • [missing_analysis] Null patterns
  • [outliers] IQR detection

TOKENS: used=350, saved=21200
```

**Total context: ~350 tokens** (vs ~27,000 without compression)
