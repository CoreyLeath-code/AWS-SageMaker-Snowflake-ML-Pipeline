# Architecture

## Runtime architecture

```mermaid
flowchart LR
    SF[Snowflake] --> MON[SnowflakeMonitorAgent]
    MON --> SUP[MLOpsSupervisor]
    SUP --> SM[SageMakerOpsAgent]
    SM --> AWS[AWS SageMaker]
    AWS --> MET[FinalMetricDataList]
    MET --> EVAL[Promotion evaluator]
    EVAL --> SUP
    SUP --> LOG[DailyLog.md]
```

## Promotion control flow

```mermaid
flowchart TD
    C[Validated config] --> Q[Query new records]
    Q --> D[Example drift hook]
    D --> T{Retraining trigger?}
    T -->|no| IDLE[Record IDLE]
    T -->|yes| JOB[Create training job]
    JOB --> DESC[Describe training job]
    DESC --> DONE{Completed?}
    DONE -->|no| REJECT[Not promotable]
    DONE -->|yes| READ[Read configured metric]
    READ --> FINITE{Metric exists and finite?}
    FINITE -->|no| REJECT
    FINITE -->|yes| THRESH{Threshold met?}
    THRESH -->|no| REJECT
    THRESH -->|yes| PASS[Promotable evidence]
```

## Boundaries

- Snowflake credentials are environment-provided.
- Snowflake row-count monitoring is live-capable; the drift method is currently an example stub returning false.
- SageMaker training submission is implemented through `boto3`.
- Job lifecycle polling/waiting is not yet a complete state machine.
- Promotion is evidence-gated but is not equivalent to deployment approval.
- CI validation is intentionally offline and should not be represented as a live-cloud integration test.
