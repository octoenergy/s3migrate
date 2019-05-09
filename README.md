[![CircleCI status](https://circleci.com/gh/octoenergy/s3migrate/tree/master.png?circle-token=xxx)](https://circleci.com/gh/octoenergy/s3migrate/tree/master)
[![codecov](https://codecov.io/gh/octoenergy/s3migrate/branch/feature%2Fadd-cod-cov/graph/badge.svg)](https://codecov.io/gh/octoenergy/s3migrate)


# s3migrate
Move
`bucket/training_data/2019-01-01/part1.parquet` to 
`bucket/data/split=training/execution_date=2019-01-01/part1.parquet`,
`bucket/validation_data/2019-06-01/part13.parquet` to 
`bucket/data/split=training/execution_date=2019-06-01/part13.parquet`,
etc.:

```
old_path = "bucket/{split}_data/{execution_date}/{filename}
new_path = "bucket/data/split={split}/execution_date={execution_date}/{filename}
s3migrate.mv(
    from=old_path,
    to=new_path,
)
```

Delete old files:
```
s3migrate.rm(
    from=old_path
)
```
