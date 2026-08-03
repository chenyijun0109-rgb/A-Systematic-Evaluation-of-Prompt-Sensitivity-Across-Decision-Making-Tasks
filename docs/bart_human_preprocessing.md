# BART Human Data Preprocessing

**Date:** 2026-06-14  
**Raw file:** `DATASET/BART/Dataset.xlsx`  
**Processed output:** `outputs/processed/human_metrics/bart_human_metrics.csv`

## Raw Sample

The local workbook has no header row and contains:

```text
5,880 rows = 147 participant IDs x 40 balloon records
```

Every participant has exactly 40 rows, split across two 20-balloon blocks.

## Age Field

The ninth Excel column, represented by zero-based index `8`, contains age:

- it is constant across all 40 rows for each participant;
- raw values range from 13 to 64;
- the retained adult sample has an age range of 18–64 and a mean age of
  approximately 30.91.

The positional mapping is explicit in code:

```text
BART_AGE_COLUMN = 8
BART_MINIMUM_AGE = 18
```

## Exclusion Rule

```text
include participant if age >= 18
```

The rule is evaluated from the age column. Participant IDs are not hard-coded
as exclusions.

| Participant ID | Age | Balloon rows | Reason |
|---:|---:|---:|---|
| 4 | 16 | 40 | `age_below_18` |
| 5 | 14 | 40 | `age_below_18` |
| 7 | 17 | 40 | `age_below_18` |
| 13 | 13 | 40 | `age_below_18` |
| 79 | 16 | 40 | `age_below_18` |
| 86 | 16 | 40 | `age_below_18` |

Therefore:

```text
147 source participants
- 6 participants younger than 18
= 141 included adult participants
```

The excluded participants account for 240 rows. The retained dataset contains
5,640 balloon rows.

## Audit Outputs

```text
outputs/processed/human_metrics/bart_human_metrics.csv
outputs/processed/human_metrics/bart_exclusions.csv
outputs/processed/human_metrics/summary.json
```

`bart_exclusions.csv` records participant ID, age, balloon count, and reason.
`summary.json` records the threshold, participant counts, excluded IDs and
ages, and row counts.

## Metrics

The filter changes sample inclusion only. The metric formulas remain:

- `average_pumps`;
- `adjusted_average_pumps`;
- `explosion_rate`;
- `average_earning_per_balloon`;
- `post_explosion_adjustment`.

`post_explosion_adjustment` averages `next balloon pumps - exploded balloon
pumps` only for explosions followed by another balloon. A participant with no
eligible transition has a missing value rather than zero. In the retained
adult sample, one participant has no eligible transition, so this metric has
an effective sample size of 140; the other BART metrics retain all 141 adults.

The 40-balloon task structure is aligned with the local dataset and Sebri et
al. (2023): https://doi.org/10.1080/20445911.2023.2181065
