# Architecture Overview

The system is designed with **DDD + Clean Architecture + CQRS**.

- **Aggregates**: Expression, StepLedger, ConstraintSet  
- **Commands**: AlignDecimals, BorrowCarry, Digitwise, Isolate, Conclude  
- **Queries**: GetTrace, CrossCheck, GetPOAV, BackSub, DiffAgainstTruth  

This ensures separation of concerns and immutable event logs.
