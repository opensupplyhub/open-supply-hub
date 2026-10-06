/**
 * Interim copy and visual tokens for satellite-detected candidate locations
 * (Earth Genome Phase 1, OSDEV-3247).
 *
 * EVERYTHING in this file is a placeholder awaiting Design review under
 * OSDEV-3192 (display treatment: unnamed-location placeholder, candidate and
 * disputed visuals). Design should be able to replace the final strings and
 * colours here without touching the components.
 */
import COLOURS from './COLOURS';

export const CANDIDATE_STATES = Object.freeze({
    UNVERIFIED: 'unverified',
    DISPUTED: 'disputed',
    CONFIRMED: 'confirmed',
    RETIREMENT_PENDING: 'retirement_pending',
});

export const CANDIDATE_VOTES = Object.freeze({
    CONFIRMED: 'confirmed',
    NOT_A_FACILITY: 'not_a_facility',
});

export const CANDIDATE_COPY = Object.freeze({
    // Badge shown wherever a candidate is rendered (panel, detail page).
    badge: 'Satellite-detected candidate',
    // Placeholder title for a candidate OS ID page (name is '' by design, D1).
    placeholderName: 'Unnamed location (satellite-detected)',
    panelTitle: 'Is there a facility here?',
    panelIntro:
        'This footprint was detected from satellite imagery and has not ' +
        'been confirmed by a person yet. Your vote helps decide whether ' +
        'it stays on the map.',
    voteFacility: 'This is a facility',
    voteNotFacility: "This isn't a facility",
    yourVote: 'Your vote',
    changeVoteHint:
        'You can change your vote at any time while voting is open.',
    votingClosed: 'Voting closed',
    votingClosedDetail:
        'This candidate has been confirmed as a facility. Use the ' +
        'contribute options to add or correct its details.',
    retired: 'This candidate was retired',
    retiredDetail:
        'The community agreed this is not a facility, so the record ' +
        'has been removed.',
    saveError: 'Your vote could not be saved. Please try again.',
    noVotesYet: 'No votes yet',
    loginTitle: 'Log in to vote',
    loginBody:
        'You must be logged in with an Open Supply Hub account to vote ' +
        'on satellite-detected candidates.',
    loginCancel: 'Cancel',
    loginAction: 'Log In',
    knowThisFacility: 'I know this facility',
    knowThisFacilityHint:
        'Add a name and address so this location can be confirmed.',
    nearbyMatchesTitle: 'Possible matches nearby',
    nearbyMatchesEmpty: 'No confirmed production locations nearby.',
    provenanceSource: 'Source',
    provenanceConfidence: 'Confidence',
    provenanceExternalId: 'External ID',
    provenanceDetected: 'Detected',
    // Design: section title used for the inline panel on the detail page.
    detailSectionTitle: 'Community validation',
    detailHiddenSectionsNote:
        'Contributor data, claims and extended fields are not shown for ' +
        'satellite-detected candidates until they are confirmed.',
});

export const CANDIDATE_STATE_LABELS = Object.freeze({
    [CANDIDATE_STATES.UNVERIFIED]: 'Unverified',
    [CANDIDATE_STATES.DISPUTED]: 'Disputed',
    [CANDIDATE_STATES.CONFIRMED]: 'Confirmed',
    [CANDIDATE_STATES.RETIREMENT_PENDING]: 'Retirement pending',
});

export const CANDIDATE_STATE_DESCRIPTIONS = Object.freeze({
    [CANDIDATE_STATES.UNVERIFIED]: 'Not enough votes yet to decide.',
    [CANDIDATE_STATES.DISPUTED]:
        'People disagree about this one. Voting stays open.',
    [CANDIDATE_STATES.CONFIRMED]: 'The community agrees this is a facility.',
    [CANDIDATE_STATES.RETIREMENT_PENDING]:
        'The community agrees this is not a facility. A moderator will ' +
        'review before it is removed.',
});

/**
 * Human-readable tally, e.g. "3 say facility · 2 say not".
 */
export const formatCandidateTally = ({
    confirmed = 0,
    not_a_facility: notAFacility = 0,
} = {}) => `${confirmed} say facility · ${notAFacility} say not`;

/**
 * Interim map styling per validation state (flagged for Design, OSDEV-3192):
 *   unverified          dashed amber outline
 *   disputed            dotted purple outline (split shown as a badge)
 *   confirmed           solid green outline
 *   retirement_pending  same as disputed, plus a "Retirement pending" label
 * Leaflet paths cannot be hatched without SVG patterns, so disputed uses a
 * distinct colour + dot pattern instead of true stripes.
 */
export const CANDIDATE_STATE_STYLES = Object.freeze({
    [CANDIDATE_STATES.UNVERIFIED]: Object.freeze({
        color: COLOURS.DARK_AMBER,
        fillColor: COLOURS.AMBER,
        dashArray: '6 4',
    }),
    [CANDIDATE_STATES.DISPUTED]: Object.freeze({
        color: COLOURS.PURPLE,
        fillColor: COLOURS.PURPLE,
        dashArray: '2 6',
    }),
    [CANDIDATE_STATES.CONFIRMED]: Object.freeze({
        color: COLOURS.DARK_GREEN,
        fillColor: COLOURS.MINT_GREEN,
        dashArray: null,
    }),
    [CANDIDATE_STATES.RETIREMENT_PENDING]: Object.freeze({
        color: COLOURS.PURPLE,
        fillColor: COLOURS.PURPLE,
        dashArray: '2 6',
    }),
});

export const CANDIDATE_BADGE_COLOURS = Object.freeze({
    background: COLOURS.AMBER_50,
    border: COLOURS.AMBER_300,
    text: COLOURS.AMBER_800,
});

export const CANDIDATE_STATE_CHIP_COLOURS = Object.freeze({
    [CANDIDATE_STATES.UNVERIFIED]: Object.freeze({
        background: COLOURS.LIGHT_AMBER,
        text: COLOURS.AMBER_800,
    }),
    [CANDIDATE_STATES.DISPUTED]: Object.freeze({
        background: COLOURS.LIGHT_PURPLE_BG,
        text: COLOURS.PURPLE_TEXT,
    }),
    [CANDIDATE_STATES.CONFIRMED]: Object.freeze({
        background: COLOURS.LIGHT_GREEN,
        text: COLOURS.GREEN_TEXT,
    }),
    [CANDIDATE_STATES.RETIREMENT_PENDING]: Object.freeze({
        background: COLOURS.LIGHT_PURPLE_BG,
        text: COLOURS.PURPLE_TEXT,
    }),
});
