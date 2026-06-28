# Provenance Guard

Provenance Guard is a Flask based web application that estimates whether submitted text is likely human written or AI-generated. Rather than relying on a single detector, the system combines two independent detection signals into one confidence score and presents users with a transparent attribution label. The system also supports creator appeals, maintains a structured audit log, and applies rate limiting to prevent abuse.

The project demonstrates that AI provenance should be treated as a confidence based decision rather than a binary classification. Users receive both the prediction and the confidence behind it, making the system more transparent and easier to challenge when mistakes occur.

# System Architecture

The system consists of the following components:

* **Flask API (app.py):** Handles all HTTP endpoints.
* **Groq LLM Detector (detector.py):** Uses a large language model to estimate how AI-like the writing appears.
* **Stylometric Detector (detector.py):** Computes a lightweight writing-style score based on vocabulary diversity, sentence variation, and punctuation usage.
* **Confidence Scoring (confidence.py):** Combines both signals into one confidence value.
* **Transparency Labels (labels.py):** Maps confidence values to user-facing explanations.
* **Audit Log (audit.py):** Stores every submission and appeal in a structured JSON log.


# Detection Signals

The system combines two independent signals.

### 1. LLM Detection

The first detector uses the Groq API with the Llama 3.3 70B model. The model receives the submitted text together with instructions to estimate whether the writing appears AI-generated or human-written. It returns a confidence value between 0 and 1.

This detector captures language patterns that are difficult to describe with handcrafted rules, such as repetitive phrasing, overly formal structure, and typical LLM writing habits.

### 2. Stylometric Analysis

The second detector uses simple stylometric features without requiring machine learning. It measures:

* Vocabulary diversity (type-token ratio)
* Sentence-length variation
* Punctuation frequency

These features provide an independent signal that complements the LLM output. Human writing often has greater variation in sentence structure and vocabulary, while AI-generated text frequently appears more uniform.


# Confidence Scoring

The final confidence score combines both detection signals:

Confidence = (0.55 × LLM Score) + (0.45 × Stylometric Score)

The confidence score is then mapped into three categories:

* **0.00 – 0.45:** Likely Human
* **0.46 – 0.64:** Uncertain
* **0.65 – 1.00:** Likely AI

Using two signals instead of one reduces dependence on the language model alone and provides more balanced decisions.

### Example Results

**High-confidence AI**

* LLM Score: 0.80
* Stylometric Score: 0.50
* Final Confidence: **0.67**
* Attribution: **Likely AI**

**Lower-confidence Human**

* LLM Score: 0.20
* Stylometric Score: 0.30
* Final Confidence: **0.25**
* Attribution: **Likely Human**

These examples demonstrate that the confidence score varies meaningfully across different inputs instead of producing nearly identical outputs.


# Transparency Labels

The API returns one of three labels.

### High Confidence AI

> Likely AI-generated. High confidence detection.

### High Confidence Human

> Likely human-written. Our analysis found strong indicators that this content was written by a human.

### Uncertain

> Uncertain. The submitted content contains both human and AI characteristics.

These labels communicate uncertainty rather than presenting the decision as absolute fact.


# Appeals Workflow

Creators may challenge a classification using the **POST /appeal** endpoint.

The endpoint:

* accepts a content ID and creator reasoning
* updates the submission status to **under_review**
* records the creator's explanation
* preserves the original detection result in the audit log

No automatic reclassification is performed. The appeal simply records the creator's request for later review.


# Audit Log

Every submission is recorded in a structured JSON audit log.

Each entry contains:

* timestamp
* content ID
* creator ID
* LLM score
* stylometric score
* confidence score
* attribution
* review status
* appeal reasoning (if submitted)

This provides a complete history of every decision made by the system.


# Rate Limiting

Flask-Limiter protects the submission endpoint.

Current limits:

* **10 submissions per minute**
* **100 submissions per day**

These limits are appropriate for normal users submitting their own work while preventing automated abuse.

Example test output:

```
200
200
200
200
200
200
200
200
200
200
429
429
```

The first ten requests succeed, while later requests are rejected with HTTP 429 (Too Many Requests).


# Known Limitations

The current system uses only two lightweight detection signals and therefore cannot perfectly distinguish human and AI writing.

One case that may produce incorrect classifications is highly polished academic writing created by a human. Such writing often resembles AI-generated text because it uses consistent sentence structure, formal vocabulary, and low stylistic variation. As a result, both the LLM detector and stylometric detector may assign higher AI scores than appropriate.

In a production deployment, I would incorporate additional signals such as document provenance metadata, cryptographic content signatures, and supervised machine learning models trained on labeled human and AI text.


# Specification Reflection

The project specification strongly influenced the overall architecture by encouraging confidence-based classification instead of simple binary decisions. This led to implementing transparency labels, confidence scoring, audit logging, and an appeals workflow rather than only returning an AI probability.

One implementation difference is the storage layer. Instead of using a database, this project stores audit records in a structured JSON file. This simplified development while still satisfying the requirement to maintain persistent records of submissions and appeals.


# AI Usage

AI tools were used throughout development, but all generated code was reviewed and modified before being integrated.

### Example 1

I prompted ChatGPT to generate the confidence-scoring function that combines the LLM detector and stylometric detector into a single confidence value.

I modified the generated code by adjusting the weighting (55% LLM and 45% stylometric) and selecting thresholds that produced meaningful variation during testing.

### Example 2

I used Cloude to generate the initial implementation of the appeal endpoint.

The generated version incorrectly appended a new log instead of updating the existing record. I revised the implementation by creating an `overwrite_log()` function so that appeals correctly update the original audit entry rather than duplicating it.


# Running the Project

Install dependencies:

```
pip install -r requirements.txt
```

Start the server:

```
python app.py
```

Submit text:

```
POST /submit
```

View audit log:

```
GET /log
```

Submit an appeal:

```
POST /appeal
```

# Demo Video
Watch the project demo here:

https://drive.google.com/file/d/1qeCV-Sz-a2YemiiKj5gFya2OrAolw4gP/view?usp=sharing

