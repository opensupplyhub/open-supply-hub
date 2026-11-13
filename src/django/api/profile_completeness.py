'''
Profile completeness prototype: an admin-only preview of how complete,
recent and widely contributed-to a production location's profile is.

The score says nothing about whether the data is correct, so nothing here
(or in what is built on it) may describe it as verified, trusted or
accurate.
'''

# Waffle flag, on for superusers and for members of the auth group of the
# same name. Everyone else gets a 404 from the endpoint.
PROFILE_COMPLETENESS_FLAG = 'show_profile_completeness'

# The eight components the scorer averages into the score, in display
# order, keyed by the scorer's own output column names.
COMPONENTS = (
    ('claimed_status', 'Claimed status'),
    ('recency_score', 'Data recency'),
    ('contribution_count_score', 'Contribution count'),
    ('contribution_mix_score', 'Contribution mix'),
    ('completeness_score', 'Field completeness'),
    ('claimed_only_score', 'Claimed-only detail'),
    ('assessments_audits_score', 'Assessments & audits'),
    ('certifications_score', 'Certifications'),
)
COMPONENT_KEYS = tuple(key for key, _ in COMPONENTS)

# PLACEHOLDER cutoffs carried over from the design mockup. They are not
# calibrated: the real ones are to be set from the score's distribution
# over the whole population. Lower bound of level 2, then of level 3.
LEVEL_CUTOFFS = (0.45, 0.70)
MAX_LEVEL = len(LEVEL_CUTOFFS) + 1


def level_for_score(score):
    '''The 1-based level (number of filled bars) a 0-1 score falls in.'''
    if score is None:
        return None
    return 1 + sum(1 for cutoff in LEVEL_CUTOFFS if score >= cutoff)


class ClassifierTiers:
    '''
    Tiers of the model-backed classification stored next to the score so
    the two can be compared. "best" only occurs on the agreement check.
    '''
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    BEST = 'best'

    FINAL = (LOW, MEDIUM, HIGH)
    AGREEMENT = (LOW, MEDIUM, HIGH, BEST)

    # The level a final tier corresponds to, for comparing it with the
    # score's level.
    LEVELS = {LOW: 1, MEDIUM: 2, HIGH: 3}
