
# Event-Driven Payment Settlement Pipeline (AWS Serverless)

## Overview

This project implements a **serverless, event-driven payment settlement pipeline** using AWS managed services. It simulates how real-world payment processors (e.g., Adyen-like systems) deliver settlement files that may arrive **late, duplicated, or out of order**, and how to process them **reliably, idempotently, and observably** without managing servers.

The pipeline ingests raw CSV settlement files, validates and transforms them, enforces idempotency, and stores analytics-ready Parquet data partitioned by settlement date.

---

## Architecture

![architectur.png](./Architecture/architecture.png)

---
## Core AWS Services

| Service            | Purpose                               |
| ------------------ | ------------------------------------- |
| Amazon S3          | Raw and processed data storage        |
| Amazon EventBridge | Event routing, decoupling, and replay |
| Amazon SQS         | Backpressure control, retries, DLQ    |
| AWS Lambda         | Stateless data processing             |
| Amazon CloudWatch  | Logs, metrics, alarms                 |
| Amazon SNS         | Operational notifications             |

---

## High-Level Flow

1. Raw settlement CSV uploaded to S3
2. S3 event routed through EventBridge
3. EventBridge delivers event to SQS
4. Lambda consumes SQS messages
5. File-level idempotency check using S3 ETag
6. Data is validated, transformed, and enriched
7. Output written as Parquet, partitioned by settlement date
8. Metrics and logs emitted to CloudWatch
9. On failure beyond retry limits, the message is sent to DLQ
10. Alarms sent through SNS if something goes wrong

---


## Key Features

- **Event-driven system design**  
  Files are processed automatically on arrival, supporting unpredictable T+N settlement deliveries without polling.

- **AWS-native, serverless processing**  
  Built entirely using managed AWS services (S3, EventBridge, SQS, Lambda) with no external state or always-on compute.

- **Failure isolation & controlled replay**  
  Transient failures are retried via SQS, permanent failures are isolated in a DLQ, and historical events can be replayed using EventBridge archives.

- **Monitoring & observability**  
  End-to-end visibility through CloudWatch logs, metrics, dashboards, and alarms for SLA and failure detection.

- **Automatic scaling with event volume**  
  Scales horizontally with file arrival rate and absorbs traffic bursts without manual intervention.

- **Partitioned Parquet output for analytics**  
  Append-only Parquet datasets partitioned by settlement date for efficient downstream querying.


---

## Tech Stack  


##### **AWS Services:** 
![Amazon S3](https://img.shields.io/badge/Amazon_S3-IBB91F?style=for-the-badge&logo=amazons3&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-F47521?style=for-the-badge&logo=awslambda&logoColor=white)
![Amazon SQS](https://img.shields.io/badge/Amazon_SQS-DD0B78?style=for-the-badge&logo=amazonsqs&logoColor=white)
![Amazon EventBridge](https://img.shields.io/badge/Amazon_EventBridge-5A2D82?style=for-the-badge&logo=amazoneventbridge&logoColor=white)
![Amazon CloudWatch](https://img.shields.io/badge/Amazon_CloudWatch-EA4C89?style=for-the-badge&logo=amazoncloudwatch&logoColor=white)
![Amazon SNS](https://img.shields.io/badge/Amazon_SNS-FF9900?style=for-the-badge&logo=amazonsns&logoColor=white)
##### **Data Processing:**
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![AWS Wrangler](https://img.shields.io/badge/AWS_Wrangler-DD1100?style=for-the-badge&logo=amazonaws)  
##### **Storage Format:** 
![CSV](https://img.shields.io/badge/CSV-56347C?style=for-the-badge)
![Parquet](https://img.shields.io/badge/Parquet-0000CC?style=for-the-badge)
##### **Language:**
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)  



---

## Case Study

A detailed walkthrough covering:

- Problem statement
- Data characteristics
- Architecture decisions
- Idempotency strategy
- Failure handling
- Monitoring & alerting
- Trade-offs
- Cost considerations
- Future improvements

📄 **Read the full case study here:**  
[`docs/case-study.md`](docs/case-study.md)

---

## Repository Structure

```text
.
├── Lambda/
│   └── handler.py
│
├── Architecture/
│   └── architecture.png/
│
├── Dashboard/
│   └── dashboard.png/
│
├── docs/
│   └── case-study.md
│
└── README.md
```

---

## Monitoring Dashboard

![dashboard.png](./Dashboard/dashboard.PNG)

The CloudWatch dashboard provides:

- Lambda invocation and error trends
- Execution duration and SLA visibility
- DLQ depth monitoring
- Near-real-time operational health

---


## Disclaimer

This project is designed for **learning and demonstration purposes**, inspired by real-world payment data pipelines, without using or exposing any proprietary or sensitive data.

<img src="https://komarev.com/ghpvc/?username=EPS-RM&color=000000"
     width="1" height="1" />