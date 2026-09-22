# Engineering Decisions

## 1. Layered architecture

The project uses separate domain, service, adapter, and API layers.

This keeps business logic independent from the web framework and makes the system easier to test and maintain.

## 2. Protocol-based model interface

The machine-learning model is accessed through a Protocol.

This allows the model implementation to be replaced without changing the service layer.

## 3. Lightweight machine-learning model

The project uses TF-IDF with Logistic Regression.

This was selected because the ticket classification problem is small, the model is fast to load, and the approach is lightweight enough for the project requirements.

## 4. Deterministic outage rule

Full service outages are forced to urgent regardless of the model prediction.

This ensures the required safety-critical behavioral rule is always satisfied.

## 5. Strict API validation

Pydantic models reject unknown fields and validate ticket values and ranges.

This prevents malformed input from reaching the prediction service and provides predictable API behavior.