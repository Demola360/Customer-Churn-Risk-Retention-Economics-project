# Measurement Plan

**Phase 7 deliverable.** This is a designed approach, not a report of
results. No real intervention campaign has run, so there's nothing to
measure yet. What follows is how success would actually be checked,
written before any campaign starts, not fitted to whatever numbers
happen to come back afterward.

---

## Why this phase exists

Phase 6 produced a ranked list of customers worth contacting and an
expected value for doing so. But "expected" is doing real work in that
sentence. The 32.5% success rate used throughout the economics
calculation is an assumption, not a measured fact. Without a plan to
check it against reality, every future decision would keep resting on
the same untested number indefinitely. This phase closes that gap.

## Primary success metric

**Churn rate among contacted customers versus a comparable
uncontacted group, measured over a 90-day follow-up window.**

Ninety days is chosen to be long enough to capture a genuine renewal or
cancellation decision, short enough to get a usable read without
waiting out the full 12-month horizon assumed in the economics
calculation.

## The core design problem, and how it's handled

Simply measuring "did contacted customers churn less than average" isn't
good enough. Contacted customers were deliberately the highest-risk
ones, so they'd be expected to churn *more* than average regardless of
whether the intervention worked, comparing them to the whole customer
base would make a working intervention look like a failure.

The fix is a **held-back control group**, drawn from the same
qualifying pool as the customers who get contacted:

1. Take the full list of customers the capacity-constrained ranking
   recommends contacting (e.g. the top 250 by net expected value).
2. Randomly split that list: roughly 80% actually get contacted
   (the treatment group), the remaining 20% are deliberately **not**
   contacted despite qualifying (the control group).
3. After 90 days, compare the churn rate of the treatment group against
   the control group. Both groups started from identical risk profiles,
   so any difference between them is attributable to the intervention
   itself, not to the two groups being different kinds of customer to
   begin with.

This is the same logic as a randomized controlled trial, applied to a
retention campaign rather than a clinical one. It's the only design that
actually isolates the intervention's effect from the fact that
high-risk customers were already going to churn at a higher rate
regardless.

## What "it worked" would look like, stated in advance

- **Primary check:** treatment group churn rate is meaningfully lower
  than control group churn rate. A two-proportion significance test
  (e.g. a chi-square or z-test for the difference between two
  proportions) would be used to check whether the gap is larger than
  could plausibly happen by chance, rather than eyeballing two
  percentages and assuming a gap is real.
- **Recalibration check:** the actual observed success rate (the share
  of contacted customers who churned in treatment but wouldn't have in
  control, estimated from the gap between the two groups) gets compared
  against the 32.5% assumption used in Phase 6. If the real number is
  meaningfully different, the economics calculation should be rerun
  with the measured rate, not the assumed one, closing the loop between
  assumption and evidence.
- **Secondary checks:** average revenue retained per contacted customer
  against the cost of contacting them, to confirm the campaign was
  economically worthwhile in practice, not just in the pre-campaign
  estimate.

## Sample size, stated honestly as a limitation

A control group needs to be large enough to detect a real difference if
one exists, not so small that a genuine effect gets lost in noise. With
roughly 50 customers held back as a control group (20% of a 250-person
campaign), this design has limited statistical power to detect small
effects reliably. A meaningfully larger campaign, or a longer
measurement window pooling several campaign cycles, would be needed
before drawing strong conclusions from a small gap between the two
groups. This is stated here as a genuine constraint, not glossed over,
since a measurement plan that can't actually detect the effect it's
looking for isn't a real measurement plan.

## What happens next, depending on the result

- **If the intervention shows a real, statistically meaningful
  reduction in churn:** scale up the contacted volume in future cycles,
  and update Phase 6's success rate assumption to the measured value.
- **If no meaningful difference shows up:** don't assume the whole
  approach failed. Check whether the intervention itself (the specific
  offer or contact method used) was the weak link, rather than the
  targeting. The model and segmentation identified genuinely high-risk,
  high-value customers correctly, per Phase 5's calibration check, so a
  failed campaign more likely means the *offer* didn't work, not that
  the *targeting* was wrong.
- **Either way:** rerun this same measurement design on the next cycle,
  rather than treating one result as final. A single 90-day window with
  a modest control group is a first read, not a conclusive verdict.

---

## What this phase deliberately does not claim

No campaign has actually run. There are no real numbers to report here,
only the design for producing them honestly once a real campaign
exists. Presenting hypothetical results as if they'd already happened
would be exactly the kind of overclaiming this project has tried to
avoid at every earlier phase.
