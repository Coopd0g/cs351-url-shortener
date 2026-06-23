# CS 351 Final Project — Serverless URL Shortener on AWS

A fully serverless URL shortening service built on AWS Lambda, API Gateway, and DynamoDB. Final project for CS 351 Cloud Computing, Summer 2026.

---

## Overview

This project implements a URL shortener using a fully serverless architecture on AWS. A user submits a long URL via a POST request and receives a shortened URL containing a 6-character alphanumeric code. Visiting the short URL triggers a 301 redirect to the original destination. No servers are managed — all compute, storage, and routing is handled by AWS managed services.

---

## Technologies Used

- **AWS Lambda** — serverless compute (Python 3.12)
- **Amazon API Gateway** — REST API entry point
- **Amazon DynamoDB** — NoSQL storage for URL mappings
- **Amazon CloudWatch** — automatic monitoring and logging
- **AWS IAM** — least-privilege execution role

---

## Setup

1. Create a DynamoDB table named `url-shortener` with partition key `short_code` (String) using on-demand capacity
2. Create an IAM role with `AWSLambdaBasicExecutionRole` and `AmazonDynamoDBFullAccess` attached
3. Deploy `shorten.py` and `redirect.py` as separate Lambda functions using the Python 3.12 runtime
4. Create a REST API in API Gateway with `POST /shorten` and `GET /{code}` routes, both using Lambda proxy integration
5. Set `TABLE_NAME` and `BASE_URL` as environment variables on the `url-shorten` function
6. Run `test_performance.py` to reproduce the latency experiment

---

## Architecture

```
User
 |
 v
Amazon API Gateway (REST)
 |-- POST /shorten --> Lambda (url-shorten) --> DynamoDB (put_item)
 |-- GET /{code}   --> Lambda (url-redirect) --> DynamoDB (get_item) --> 301 Redirect

CloudWatch: monitors both Lambda functions automatically
IAM Role: grants Lambda minimal permissions to DynamoDB + CloudWatch Logs
```

---

## Estimated AWS Cost

| Service | Free Tier | Expected Usage |
|---|---|---|
| Lambda | 1M requests/month | ~100 requests → $0.00 |
| API Gateway | 1M calls/month | ~100 calls → $0.00 |
| DynamoDB | 25GB storage + 25 RCU/WCU | Tiny table → $0.00 |
| CloudWatch | 5GB logs/month | Minimal → $0.00 |

**Total estimated cost: $0.00** (well within AWS Free Tier)
