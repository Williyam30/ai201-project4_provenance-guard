# Provenance Guard

Provenance Guard is a Flask based backend API that estimates whether submitted text is more likely to be human written or AI generated. Rather than making absolute decisions, the system combines multiple independent detection signals to calculate a confidence score. The result is translated into a plain language transparency label for users. Every prediction is stored in a structured audit log, and creators may submit appeals if they believe their work has been incorrectly classified. The primary goal is to provide transparency while acknowledging that AI detection is inherently uncertain.

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

**What it measures**

This signal analyzes the overall writing style, semantic coherence, fluency, and language patterns of the submitted text.

Output ->  A confidence value between 0.0 and 1.0, where values closer to 1 indicate stronger evidence that the text is AI-generated.

Example: 0.82

**Why it helps**

Large language models recognize complex linguistic patterns that are difficult to capture using simple statistical methods.

**Blind Spot**

The model may confidently misclassify highly polished human writing or edited AI-generated content.


### Signal 2 — Stylometric Heuristics

**What it measures**
The system computes measurable writing statistics including:
- Vocabulary diversity
- Sentence length variation
- Punctuation density

Output -> A normalized score between 0.0 and 1.0, where higher values indicate writing patterns that appear more AI-like.

Example: 0.67

**Why it helps**

Human writing often contains greater variability, while AI generated writing tends to be more statistically uniform.

**Blind Spot**

Stylometric features alone cannot determine authorship because experienced writers and carefully edited AI content may produce similar statistics.


## False Positive Scenario

A human author submits an original poem.

The Groq model predicts AI generated, but the stylometric analysis appears more human-like.

Instead of returning a high confidence AI result, the confidence score decreases and the system returns an "Uncertain" transparency label.

The creator may submit an appeal explaining why they believe the work is original.

The appeal updates the submission status to "Under Review" and is stored in the audit log.

## Confidence Scoring and Uncertainty

Both signals return values between 0.0 and 1.0.

The final confidence score is calculated using a weighted average.

Groq LLM: 60%
Stylometric heuristics: 40%

Final Confidence = (Groq × 0.60) + (Stylometry × 0.40)

The resulting confidence determines the final classification.

Confidence	Classification
0.00–0.39	Likely Human
0.40–0.60	Uncertain
0.61–1.00	Likely AI

A confidence score of 0.60 means the available evidence is mixed. The system does not have sufficient certainty to confidently classify the text as either AI-generated or human-written, so it presents an "Uncertain" result rather than forcing a binary decision.

## Transparency Label Design

### High-Confidence AI

***Likely AI-generated***

Our analysis found strong indicators that this content was generated using an AI writing system.

***Confidence: High***

This result is an automated estimate and may be appealed if you believe it is incorrect.

### High-Confidence Human

***Likely Human-written***

Our analysis found strong indicators that this content was written by a human author.

***Confidence: High***

No automated system is perfect. If you believe this result is incorrect, you may request a review.

### Uncertain

***Uncertain***

The submitted content contains characteristics commonly found in both human-written and AI-generated text.

***Confidence: Moderate***

The system cannot make a confident determination. Additional review may be appropriate.


## Appeals Workflow

Any creator whose content has been analyzed may submit an appeal.

The appeal request includes:

- Submission ID
- Appeal reason
- Timestamp

When an appeal is received, the system:

1. Stores the creator's explanation.
2. Changes the submission status to Under Review.
3. Records the appeal in the structured audit log.

A human reviewer would see:

- Original submitted text
- Original prediction
- Confidence score
- Detection signal values
- Creator's appeal explanation
- Current review status
- Submission timestamp

## Anticipated Edge Cases

### Edge Case 1

A poem that intentionally uses repetitive language and very simple vocabulary may resemble AI-generated writing according to stylometric measurements even though it was written by a human.

### Edge Case 2

A human author who edits AI-generated text extensively may produce writing that appears highly human-like, reducing the confidence of the detector.

### Edge Case 3

Very short submissions (one or two sentences) provide insufficient information for both detection signals and will naturally produce lower confidence scores.


## API Endpoints

### POST /submit

Input

```json
{
  "text":"User submitted content"
}

Output

{
  "submission_id":1,                # Prediction
  "prediction":"Likely AI",         # Confidence score
  "confidence":0.81,                # Transparency label
  "label":"Likely AI-generated..."  # Submission ID
}

### POST /appeal

Input

{
  "submission_id":1,
  "reason":"I wrote this story myself."
}

Output

{
  "status":"Under Review",       # Updated status
  "message":"Appeal submitted."  # Confirmation message
}

### GET /log
Returns the structured audit log containing all attribution decisions and appeals.

### GET /
Returns simple API status message.

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

The submission flow begins when a user submits text through the /submit endpoint. The system validates the request, analyzes the text using two independent detection signals, combines the results into a confidence score, generates a transparency label, records the decision in the audit log, and returns the response.

The appeal flow allows creators to challenge a classification. The appeal records the creator's explanation, changes the submission status to Under Review, stores the appeal in the audit log, and returns a confirmation response.

