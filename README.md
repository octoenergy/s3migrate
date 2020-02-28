[![CircleCI](https://circleci.com/gh/octoenergy/s3migrate.svg?style=svg)](https://circleci.com/gh/octoenergy/s3migrate)
[![codecov](https://codecov.io/gh/octoenergy/s3migrate/branch/master/graph/badge.svg)](https://codecov.io/gh/octoenergy/s3migrate)

# s3migrate
Bulk delete/copy/move files or modify Hive/Drill/Athena partitions using pythonic pattern matching 

## Example

Imagine we have a dataset as follows:
```
s3://bucket/training_data/2019-01-01/part1.parquet 
s3://bucket/validation_data/2019-06-01/part13.parquet
... 
```

To make this dataset Hive-friendly, we want to includ explicit key-value pairs in the paths, e.g.:
```
s3://bucket/data/split=training/execution_date=2019-01-01/part1.parquet
s3://bucket/data/split=training/execution_date=2019-06-01/part13.parquet
...
```

This can be achieved using the `s3migrate.mv` (aka `move`) command with intutitive pattern matching:

```python
old_path = "s3://bucket/{split}_data/{execution_date}/{filename}"
new_path = "s3://bucket/data/split={split}/execution_date={execution_date}/{filename}"
s3migrate.mv(
    from=old_path,
    to=new_path,
    dryrun=False
)
```

If instead we want to delete all files matching `old_path` pattern, we can use `s3migrate.rm`:

```python
s3migrate.rm(
    from=old_path,
    dryrun=False
)
```

## Supported commands
### File-system-like operations
The module provides the following commands:

|command|number of patterns|action|
|---|---|---|
|`cp`/`copy`|2|copy (duplicate) all matched files to new location|
|`mv`/`move`|2|move (rename) all matched files|
|`rm`/`remove`|1| remove all matched files|

Eeach takes one or two patterns, as well as the `dryrun` argument.

> **NB** when two patterns are provided, both must contain the same set of keys

### General-purpose generators
| command | usecase |
| --- | --- |
| `iter`| iterate over all matching filenames, e.g. to read each file |
| `iterformats` | iterate over all matched `format dictionaries`, e.g. to collect all Hive key values |

`s3migrate.iter(pattern)` will yield file names `filename` matching `pattern`. This allows custom file processing logic downstream.

`s3migrate.iterformats(pattern)` will instead yield dictionaries `fmt_dict` such that `pattarn.format(**fmt_dict)` is equivalent to the matched `filename`.

## Dry run mode
Dry run mode allows testing your patterns without performing any destructive operations.

With `dryrun=True` (default), information about operations to be performed is logged at `INFO` and `DEBUG` level - make sure
to set your logging accordingly, e.g. inside a Jupyter Notebook:


```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers = [logging.StreamHandler()]
```
