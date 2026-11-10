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

/**
 * "I know this facility" links a candidate into the SLC update flow, but
 * Phase 1 has no promotion path: the v1 PATCH answers 404 for a candidate,
 * so the link is a dead end. Hidden until the candidate -> facility
 * promotion follow-up ships (OSDEV-2566 epic; see
 * doc/prototypes/earth-genome/option3-implementation-plan.md, "graduates via
 * SLC enrichment"). The code path stays wired so flipping this is the only
 * change needed.
 */
export const CANDIDATE_SLC_ENRICHMENT_ENABLED = false;

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
        'Votes are no longer being accepted for this candidate.',
    retired: 'This candidate was retired',
    retiredDetail:
        'The community agreed this is not a facility, so the record ' +
        'has been removed.',
    saveError: 'Your vote could not be saved. Please try again.',
    sessionPending: 'Checking your session…',
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
    viewCandidatePage: 'View candidate page',
    showMatchOnMap: 'Show on map',
    hideMatchFromMap: 'Hide from map',
    sameFacility: 'Yes, same facility',
    sameFacilityHint:
        'Counts as a "this is a facility" vote. Linking the two records ' +
        'is a moderator step.',
    tooltipHint: 'Click for details',
    // Design: section title used for the inline panel on the detail page.
    detailSectionTitle: 'Community validation',
    detailHiddenSectionsNote:
        'Contributor data, claims and extended fields are not shown for ' +
        'satellite-detected candidates until they are confirmed.',
});

/**
 * Copy for the candidate review page at /candidates (OSDEV-3755).
 * Interim wording, same Design caveat as CANDIDATE_COPY.
 */
export const CANDIDATE_LIST_COPY = Object.freeze({
    title: 'Satellite detections to review',
    intro:
        'Production locations detected from satellite imagery that have ' +
        'not been confirmed by a person yet. Sort and filter to pick an ' +
        'order, then open a detection to vote without leaving the list.',
    loginNote:
        'Log in with an Open Supply Hub account to review satellite ' +
        'detections.',
    filtersTitle: 'Filters',
    filterState: 'Validation state',
    filterConfidence: 'Confidence (%)',
    filterConfidenceMin: 'Min',
    filterConfidenceMax: 'Max',
    filterNearby: 'Confirmed facility within 500 m',
    filterNearbyAny: 'Any',
    filterNearbyYes: 'Has one',
    filterNearbyNo: 'Has none',
    filterCountry: 'Country codes',
    filterCountryHint: 'ISO alpha-2, comma-separated (e.g. US, MX)',
    filterArea: 'Map area',
    filterAreaNone: 'Draw a rectangle on the map to limit the list.',
    filterAreaSet: 'Limited to the drawn area',
    filterAreaClear: 'Clear area',
    resetFilters: 'Reset filters',
    columnOsId: 'OS ID',
    columnConfidence: 'Confidence',
    columnState: 'State',
    columnVotes: 'Votes',
    columnNearby: 'Nearby',
    columnNearest: 'Nearest confirmed facility',
    columnCountry: 'Country',
    nearestNone: 'None within 500 m',
    noVotes: 'No votes',
    empty: 'No satellite detections match these filters.',
    pagePastEnd: 'That page is past the end of the list.',
    backToFirstPage: 'Back to the first page',
    loadError: 'The list could not be loaded. Please try again in a moment.',
    retry: 'Retry',
    mapDraw: 'Draw area',
    mapDrawCancel: 'Cancel drawing',
    mapDrawHint: 'Click and drag on the map to draw a rectangle.',
    mapLegend: 'Dots are the detections on this page',
    panelPrevious: 'Previous',
    panelNext: 'Next',
    panelPosition: (index, total) => `${index} of ${total} on this page`,
    panelClose: 'Close',
    countSummary: (count, page, pages) =>
        count === 0
            ? 'No detections'
            : `${count.toLocaleString()} detection${
                  count === 1 ? '' : 's'
              } · page ${page} of ${pages}`,
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
    [CANDIDATE_STATES.CONFIRMED]:
        'The community agrees this is a facility. Voting stays open, so ' +
        'later votes can still change this.',
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
