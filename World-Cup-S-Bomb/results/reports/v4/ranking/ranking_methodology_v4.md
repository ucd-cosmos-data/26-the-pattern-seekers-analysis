# Qatar 2022 Outfield Tournament Impact v4 — Methodology

Active model: `outfield-tournament-impact-v4+goalkeeper-event-profile-v3`.

Tournament Impact v4 is an evidence-accumulating tournament total. It contains no advancement, round-reached, winner, nationality, identity, award, reputation, or target-rank feature.

The defensive channel is opposition-adjusted before adding validated off-ball prevention. Per-channel reliability then shrinks limited evidence before variance rescaling. Only the post-adjustment, post-prevention, post-shrinkage channel may be rescaled. Continuous attacking and defending orientation weights sum to one and are bounded away from zero and one.

Predominant position and continuous sub-role are reporting frames, not score bonuses. High-minute contribution receives more evidential support through accumulated actions and reliability only.

The six-field publication retains the supplied monotonic FIFA-style 55--99 score with one decimal. Raw model fields remain available in the rich tables and player packets.

Goalkeepers retain their validated v3 publication bridge; only the 553 eligible outfield rows are rescored by this outfield-v4 model. Backup goalkeepers remain unranked.
