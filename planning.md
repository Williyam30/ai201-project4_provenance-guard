# Provenance Guard

Provenance Guard is a Flask-based backend API that analyzes submitted text to estimate whether it is likely human-written or AI-generated. Instead of relying on a single detector, the system combines multiple independent signals to produce a confidence score, generates a transparency label for users, records every decision in an audit log, and provides an appeals process when creators disagree with the result. The goal is to communicate uncertainty honestly rather than making absolute claims.

## Architecture Narrative

When a user submits text through the POST /submit endpoint, the API first validates the request and checks whether the user has exceeded the rate limit.

- If the request is accepted, the text enters the multi signal detection pipeline.

- The first signal uses the Groq Llama model to analyze the overall writing style and estimate whether the text appears human-written or AI generated.

- The second signal performs stylometric analysis using Python by measuring vocabulary diversity, sentence length variation, and punctuation density.

- Both signals produce individual scores.

The confidence scoring component combines these scores into one overall confidence value.

The transparency label generator converts the prediction into language that ordinary users can understand.

Before the response is returned, every prediction is stored in the structured audit log.

If the creator believes the prediction is incorrect, they may submit an appeal using POST /appeal.

The appeal records the creator's explanation, updates the submission status to "Under Review", and appends the appeal to the audit log.


## Detection Signals

### Signal 1 — Groq LLM

**Property measured**

Overall semantic consistency, writing style, and language patterns.

**Why it helps**

Large language models recognize many patterns that distinguish AI-generated writing from human writing.

**Blind Spot**

Highly polished human writing or heavily edited AI text may confuse the model.


### Signal 2 — Stylometric Heuristics

**Property measured**

- Vocabulary diversity
- Sentence length variation
- Punctuation density

**Why it helps**

Human writing usually contains more variation than AI-generated writing.

**Blind Spot**

Statistical writing features alone cannot determine authorship.


## False Positive Scenario

A human author submits an original poem.

The Groq model predicts AI generated, but the stylometric analysis appears more human-like.

Instead of returning a high confidence AI result, the confidence score decreases and the system returns an "Uncertain" transparency label.

The creator may submit an appeal explaining why they believe the work is original.

The appeal updates the submission status to "Under Review" and is stored in the audit log.


## API Endpoints

### POST /submit

Input

```json
{
  "text":"User submitted content"
}

Output

{
  "submission_id":1,
  "prediction":"Likely AI",
  "confidence":0.81,
  "label":"Likely AI-generated..."
}

### POST /appeal

Input

{
  "submission_id":1,
  "reason":"I wrote this story myself."
}

Output

{
  "status":"Under Review",
  "message":"Appeal submitted."
}

### GET /log
Returns the audit log.

### GET /
Returns API status.

## Architecture
 
                        User
                        |
                   POST /submit
                        |
                   Raw submitted text
                        |
                   Input Validation
                        |
                   Flask Rate Limiter Check
                        |
                   Multi-Signal Detection
                   |                    |
               Groq LLM          Stylometric Analysis
                            |
                        Individual Scores
                            |
                        Confidence Calculator
                            |
                        Combined Confidence
                            |
                        Transparency Label Generator
                            |
                        Label Text
                            |
                        Structured Audit Log
                            |
                        Save Prediction
                            |
                        JSON Response

## Appeal Flow

                        Creator
                           |
                        POST /appeal
                           |
                        Submission ID + Reason
                           |
                        Update Status "Under Review"
                           |
                        Append Audit Log
                           |
                        JSON Response

