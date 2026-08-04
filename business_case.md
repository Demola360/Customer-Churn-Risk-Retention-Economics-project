# Customer Churn Risk & Retention Economics — Business Case

**Phase 1 deliverable.** This document exists before any SQL, model, or
dashboard work starts — the business problem is defined first, the
technical work exists to answer it.

---

## Central question

Not *"which customers will churn"* — that question alone doesn't lead to
a decision. This project answers three things together:

1. **Which customers should we prioritise for retention?**
2. **What intervention makes economic sense for them?**
3. **How would we measure whether it worked?**

A model that ranks customers by churn risk but never connects to cost,
value, or a measurement plan is a statistics exercise, not a business
recommendation. All three questions get an answer here.

---

## Stakeholders

| Stakeholder | Need |
|---|---|
| **Retention Manager** | A prioritised, explainable list of which customers to contact, and why |
| **Finance / Commercial Lead** | Confidence that the cost of intervening is justified by the expected retained value — i.e. is this worth doing at all, and for which customers specifically |

These two stakeholders don't automatically agree. The Retention Manager's
default instinct is to contact every at-risk customer; the Finance Lead's
job is to ask where that stops being worthwhile. The intervention
economics phase exists specifically to resolve that tension with a
number, not an opinion.

---

## Business problem

A telecom provider loses customers every month. Without a consistent,
evidence-based way to identify which customers are both **likely to
leave** and **worth the cost of trying to retain**, retention spend is
either applied too broadly (wasted on low-value or low-risk customers)
or not applied at all (high-value at-risk customers churn unnoticed).

## Data source

**IBM Telco Customer Churn dataset** — approximately 7,000 real,
anonymized customer records from a telecom provider, including tenure,
contract type, monthly and total charges, service subscriptions, and a
genuine churn outcome (`Yes`/`No`) for each customer. This is real
company data, not simulated — the previous project's most-repeated
criticism (fictional client-level data) doesn't apply here. It is a
historical snapshot, not a live daily feed; no publicly available
customer-level dataset updates in real time, for the same confidentiality
reasons discussed on the last project.

## Churn definition

Churn is defined exactly as the dataset defines it: **a customer who
left the service within the last billing period, as recorded in the
`Churn` field.** This is a genuine, disclosed outcome label — not a
hidden "answer key" used to validate a rule-based score after the fact,
which was a specific weakness of the previous project's methodology.
Because this is a real, defined label, an actual predictive model can be
trained and evaluated against it honestly.

---

## User stories

> As a Retention Manager, I want a ranked, explainable list of at-risk
> customers, so that my team can prioritise outreach instead of treating
> every account equally.

> As a Finance Lead, I want to know the expected cost and expected
> retained value of intervening on each customer segment, so that I can
> approve spend where it's justified and decline it where it isn't.

> As either stakeholder, I want a defined way to measure whether an
> intervention campaign actually worked, so that the approach can be
> validated or corrected in future cycles — not just launched and
> forgotten.

---

## Functional requirements

| ID | Requirement |
|---|---|
| FR01 | System shall segment customers by churn risk and customer value |
| FR02 | System shall rank customers within each segment by predicted churn probability |
| FR03 | System shall show the primary factors driving each customer's churn risk |
| FR04 | System shall estimate expected retained value vs. intervention cost per segment |
| FR05 | System shall recommend whether intervention is economically justified, per segment |
| FR06 | System shall define a measurement approach for evaluating intervention success |
| FR07 | User shall filter and explore customers by segment, risk, and value in Power BI |

## Non-functional requirements

- Model and business logic must be explainable to a non-technical
  stakeholder without a statistics background
- All financial assumptions (intervention cost, customer value) must be
  stated explicitly as assumptions, not presented as measured fact
- No real customer-identifying information is exposed (the dataset is
  already anonymized at source)

---

## Business rules (to be finalised in later phases)

Rules for risk tier, value tier, and intervention recommendation will be
defined once the model and cohort analysis exist — stating them now, before
the data has been explored, would be exactly the kind of unjustified
assumption the previous project was criticised for. This section gets
filled in during Phase 5 (segmentation) and Phase 6 (economics), not now.

---

## Assumptions

- Historical churn patterns in this dataset are assumed to be reasonably
  representative of near-term future risk — a standard assumption for any
  churn model, stated explicitly rather than left implicit
- Intervention cost and customer lifetime value will be modelled using
  stated, defensible assumptions (e.g. estimated from `MonthlyCharges`
  and `tenure`) since the dataset does not include actual intervention
  cost data — no real telecom's actual retention budget is known or
  claimed
- The measurement plan (Phase 7) is a **designed approach**, not executed
  results — there is no live intervention to measure the outcome of

## As-is

Retention decisions, if made at all, are not based on a consistent,
evidence-based prioritisation of risk against value.

## To-be

Customers are segmented by risk and value, ranked within segment, and
matched to a recommended action only where the economics justify it —
with a defined method for checking whether that recommendation actually
worked.

---

## Scope boundaries — what this project does not do

- Does not claim to predict individual customer behaviour with certainty
  — it estimates probability and ranks accordingly
- Does not execute or observe a real intervention campaign — the
  economics and measurement plan are designed, not results
- Does not use live or daily-updating data — this is a fixed historical
  dataset, consistent with how real churn analytics projects are
  typically conducted (periodic batch analysis, not live monitoring)
