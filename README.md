## cs351-url-shortener
## Serverless URL Shortener on AWS

---

## Prerequisites
- AWS account with Console access
- Python 3.x installed locally

---

## Step 1 — Create the DynamoDB Table

1. Go to **AWS Console → DynamoDB → Create table**
2. Table name: `url-shortener`
3. Partition key: `short_code` (String)
4. Table settings: **On-demand** (pay per request, free tier friendly)
5. Click **Create table** — wait for status to show Active

---

## Step 2 — Create the IAM Role for Lambda

1. Go to **IAM → Roles → Create role**
2. Trusted entity type: **AWS service** → Lambda
3. Attach permissions:
   - `AWSLambdaBasicExecutionRole` (for CloudWatch logs)
   - `AmazonDynamoDBFullAccess` (for read/write to your table)
4. Role name: `lambda-url-shortener-role`
5. Click **Create role**

---

## Step 3 — Deploy the Shorten Lambda

1. Go to **Lambda → Create function**
2. Function name: `url-shorten`
3. Runtime: **Python 3.12**
4. Execution role: Use existing → `lambda-url-shortener-role`
5. Click **Create function**
6. In the **Code** tab, replace the default code with contents of `shorten.py`
7. Click **Deploy**
8. Go to **Configuration → Environment variables → Edit**:
   - `TABLE_NAME` = `url-shortener`
   - `BASE_URL` = (fill in after Step 4)

---

## Step 4 — Deploy the Redirect Lambda

1. Repeat Step 3 but:
   - Function name: `url-redirect`
   - Paste contents of `redirect.py`
2. Add environment variable: `TABLE_NAME` = `url-shortener`
3. Click **Deploy**

---

## Step 5 — Create the API Gateway

1. Go to **API Gateway → Create API → REST API → Build**
2. API name: `url-shortener-api`
3. Click **Create API**

**Create POST /shorten route:**
1. Actions → **Create Resource** → Resource name: `shorten`
2. Select `/shorten` → Actions → **Create Method** → POST
3. Integration type: Lambda Function → `url-shorten`
4. Click Save → OK to grant permission

**Create GET /{code} route:**
1. Select `/` → Actions → **Create Resource**
   - Resource name: `{code}` (with curly braces — this is a path parameter)
2. Select `/{code}` → Actions → **Create Method** → GET
3. Integration type: Lambda Function → `url-redirect`
4. Click Save → OK

**Enable CORS (for POST /shorten):**
1. Select `/shorten` → Actions → **Enable CORS** → Enable CORS and replace existing

**Deploy the API:**
1. Actions → **Deploy API**
2. Stage name: `prod`
3. Copy the **Invoke URL** shown (looks like `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

---

## Step 6 — Update the BASE_URL Environment Variable

1. Go back to the `url-shorten` Lambda
2. Configuration → Environment variables → Edit
3. Set `BASE_URL` = your Invoke URL (from Step 5)
4. Save

---

## Step 7 — Test with curl

**Shorten a URL:**
```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://aws.amazon.com/lambda/features/"}'
```

Expected response:
```json
{
  "short_url": "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/AbCd1Z",
  "code": "AbCd1Z",
  "original_url": "https://aws.amazon.com/lambda/features/"
}
```

**Test the redirect (paste in browser or use -L flag):**
```bash
curl -L https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/AbCd1Z
```

---

## Step 8 — Run the Performance Test

```bash
pip install requests
# Edit test_performance.py and set BASE_URL to your Invoke URL
python test_performance.py
```

---

## Step 9 — View CloudWatch Metrics

1. Go to **CloudWatch → Log groups**
2. Find `/aws/lambda/url-shorten` and `/aws/lambda/url-redirect`
3. View invocation logs, duration, and errors

For metrics dashboard:
- CloudWatch → Metrics → Lambda → By Function Name
- Track: Invocations, Duration, Errors, Throttles

---

## Architecture Summary

```
User
 │
 ▼
Amazon API Gateway (REST)
 ├── POST /shorten ──→ Lambda (url-shorten) ──→ DynamoDB (put_item)
 └── GET /{code}  ──→ Lambda (url-redirect) ──→ DynamoDB (get_item) ──→ 301 Redirect
 
CloudWatch: monitors both Lambda functions automatically
IAM Role: grants Lambda minimal permissions to DynamoDB + CloudWatch Logs
```

---

## Estimated AWS Cost (Free Tier)

| Service | Free Tier | Expected Usage |
|---|---|---|
| Lambda | 1M requests/month | ~100 requests → $0.00 |
| API Gateway | 1M calls/month | ~100 calls → $0.00 |
| DynamoDB | 25GB storage + 25 RCU/WCU | Tiny table → $0.00 |
| CloudWatch | 5GB logs/month | Minimal → $0.00 |

**Total estimated cost: $0.00** (well within free tier)
