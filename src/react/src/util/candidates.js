/**
 * Helpers for satellite-detected candidate locations (OSDEV-3247).
 *
 * Backend contract (OSDEV-3245 votes, OSDEV-3249 detail responses):
 *   GET  /api/v1/production-locations/candidates/?bbox=minLng,minLat,maxLng,maxLat&limit=200
 *        -> GeoJSON FeatureCollection; feature.properties =
 *           { os_id, confidence, source, state, tally, centroid }
 *   GET  /api/v1/production-locations/{os_id}/
 *        -> candidate detail incl. validation { state, tally, your_vote,
 *           voting_open } and suggested_matches
 *   GET/POST /api/v1/production-locations/{os_id}/candidate-votes/
 *        -> { os_id, your_vote, tally, state }; POST body { vote }
 *   Legacy GET /api/facilities/{os_id}/ -> Feature whose properties carry
 *        is_candidate: true and a `candidate` object with the same content.
 */
import get from 'lodash/get';

import { maxVectorTileFacilitiesGridZoom } from './constants.facilitiesMap';
import {
    CANDIDATE_STATES,
    CANDIDATE_STATE_STYLES,
    CANDIDATE_VOTES,
} from './candidateCopy';

// Individual facility markers appear above the grid zoom; candidates follow
// the same threshold so the two layers switch on together.
export const CANDIDATE_LAYER_MIN_ZOOM = maxVectorTileFacilitiesGridZoom + 1;
export const CANDIDATE_LAYER_LIMIT = 200;
export const CANDIDATE_LAYER_DEBOUNCE_MS = 300;

const BBOX_PRECISION = 6;

const round = value => Number(Number(value).toFixed(BBOX_PRECISION));

/**
 * Leaflet LatLngBounds -> "minLng,minLat,maxLng,maxLat".
 * Accepts anything with getWest/getSouth/getEast/getNorth.
 */
export const formatBbox = bounds =>
    [
        round(bounds.getWest()),
        round(bounds.getSouth()),
        round(bounds.getEast()),
        round(bounds.getNorth()),
    ].join(',');

export const makeCandidatesBboxURL = (bbox, limit = CANDIDATE_LAYER_LIMIT) =>
    `/api/v1/production-locations/candidates/?bbox=${bbox}&limit=${limit}`;

export const makeCandidateDetailURL = osId =>
    `/api/v1/production-locations/${osId}/`;

export const makeCandidateVotesURL = osId =>
    `/api/v1/production-locations/${osId}/candidate-votes/`;

export const shouldFetchCandidates = zoom =>
    typeof zoom === 'number' && zoom >= CANDIDATE_LAYER_MIN_ZOOM;

export const isVotingOpenForState = state =>
    state !== CANDIDATE_STATES.CONFIRMED;

const emptyTally = () => ({
    [CANDIDATE_VOTES.CONFIRMED]: 0,
    [CANDIDATE_VOTES.NOT_A_FACILITY]: 0,
});

export const normalizeTally = tally => ({
    ...emptyTally(),
    [CANDIDATE_VOTES.CONFIRMED]: Number(
        get(tally, CANDIDATE_VOTES.CONFIRMED, 0) || 0,
    ),
    [CANDIDATE_VOTES.NOT_A_FACILITY]: Number(
        get(tally, CANDIDATE_VOTES.NOT_A_FACILITY, 0) || 0,
    ),
});

export const totalVotes = tally => {
    const normalized = normalizeTally(tally);
    return (
        normalized[CANDIDATE_VOTES.CONFIRMED] +
        normalized[CANDIDATE_VOTES.NOT_A_FACILITY]
    );
};

const firstDefined = (...values) => values.find(value => value !== undefined);

/**
 * Normalized validation block used by the panel. Accepts either the API
 * shape (`your_vote`, `voting_open`) or an already-normalized block
 * (`yourVote`, `votingOpen`), so it is safe to apply twice.
 * `yourVote` is `undefined` when the payload did not say (bbox features),
 * `null` when the server said the user has not voted.
 */
export const normalizeValidation = (validation = {}) => {
    const source = validation || {};
    const state = source.state || CANDIDATE_STATES.UNVERIFIED;
    const votingOpen = firstDefined(source.voting_open, source.votingOpen);
    const yourVote = firstDefined(source.your_vote, source.yourVote);
    return {
        state,
        tally: normalizeTally(source.tally),
        yourVote,
        votingOpen:
            typeof votingOpen === 'boolean'
                ? votingOpen
                : isVotingOpenForState(state),
    };
};

const normalizeSuggestedMatches = matches =>
    Array.isArray(matches)
        ? matches
              .filter(match => match && match.os_id)
              .map(match => ({
                  osId: match.os_id,
                  name: match.name || '',
                  address: match.address || '',
                  distanceM:
                      typeof match.distance_m === 'number'
                          ? match.distance_m
                          : null,
              }))
        : [];

/**
 * Normalized candidate shape consumed by CandidateValidationPanel:
 * { osId, source, confidence, externalId, createdAt, coordinates,
 *   countryName, validation, suggestedMatches, isDetailLoaded }
 */
export const normalizeCandidateDetail = detail => {
    if (!detail || !detail.os_id) return null;
    return {
        osId: detail.os_id,
        source: detail.source || null,
        confidence:
            typeof detail.confidence === 'number' ? detail.confidence : null,
        externalId: detail.external_id || null,
        createdAt: detail.created_at || null,
        coordinates: detail.coordinates || null,
        countryName: get(detail, 'country.name', null),
        validation: normalizeValidation(detail.validation),
        suggestedMatches: normalizeSuggestedMatches(detail.suggested_matches),
        isDetailLoaded: true,
    };
};

/**
 * A bbox-layer feature carries only the tally and state; `your_vote` and
 * suggested matches are fetched on demand by the panel.
 */
export const normalizeCandidateFeatureProperties = properties => {
    if (!properties || !properties.os_id) return null;
    return {
        osId: properties.os_id,
        source: properties.source || null,
        confidence:
            typeof properties.confidence === 'number'
                ? properties.confidence
                : null,
        externalId: null,
        createdAt: null,
        coordinates: properties.centroid || null,
        countryName: null,
        validation: normalizeValidation({
            state: properties.state,
            tally: properties.tally,
        }),
        suggestedMatches: [],
        isDetailLoaded: false,
    };
};

/**
 * Legacy /api/facilities/{os_id}/ Feature -> normalized candidate, or null
 * when the feature is not a candidate.
 *
 * Shared contract (FacilityCandidateDetailsSerializer, OSDEV-3249):
 * `properties.candidate = { source, external_id, confidence, polygon,
 * suggested_matches, created_at, validation: { state, tally, your_vote,
 * voting_open } }`. A payload that spreads the validation keys flat onto
 * `candidate` (the pre-contract shape) is accepted too, so either shape
 * renders.
 */
export const getCandidateFromFacilityPayload = feature => {
    if (!get(feature, 'properties.is_candidate')) return null;
    const candidate = get(feature, 'properties.candidate', {}) || {};
    const osId = get(feature, 'properties.os_id') || feature.id;
    const coordinates = get(feature, 'geometry.coordinates');
    const validation = candidate.validation || {
        state: candidate.state,
        tally: candidate.tally,
        your_vote: candidate.your_vote,
        voting_open: candidate.voting_open,
    };
    return normalizeCandidateDetail({
        os_id: osId,
        source: candidate.source,
        confidence: candidate.confidence,
        external_id: candidate.external_id,
        created_at:
            candidate.created_at ||
            get(feature, 'properties.created_from.created_at') ||
            null,
        coordinates:
            Array.isArray(coordinates) && coordinates.length >= 2
                ? { lat: coordinates[1], lng: coordinates[0] }
                : null,
        country: {
            name:
                get(feature, 'properties.country_name') ||
                get(candidate, 'country.name') ||
                null,
        },
        validation,
        suggested_matches: candidate.suggested_matches,
    });
};

/**
 * Optimistic tally after `user` changes their vote from `previousVote`
 * (null/undefined when they had none) to `nextVote`.
 */
export const applyVoteToTally = (tally, previousVote, nextVote) => {
    const next = normalizeTally(tally);
    if (previousVote === nextVote) return next;
    if (previousVote && next[previousVote] > 0) {
        next[previousVote] -= 1;
    }
    if (nextVote) {
        next[nextVote] += 1;
    }
    return next;
};

export const formatConfidence = confidence =>
    typeof confidence === 'number' ? `${Math.round(confidence * 100)}%` : '—';

export const formatDistance = distanceM => {
    if (typeof distanceM !== 'number') return '';
    if (distanceM < 1000) return `${Math.round(distanceM)} m`;
    return `${(distanceM / 1000).toFixed(1)} km`;
};

const BASE_PATH_STYLE = Object.freeze({
    weight: 2,
    opacity: 0.95,
    fillOpacity: 0.15,
});

/**
 * Leaflet path options for a candidate feature.
 */
export const getCandidateStyle = (
    state,
    { hover = false, selected = false } = {},
) => {
    const stateStyle =
        CANDIDATE_STATE_STYLES[state] ||
        CANDIDATE_STATE_STYLES[CANDIDATE_STATES.UNVERIFIED];
    let { weight } = BASE_PATH_STYLE;
    if (selected) {
        weight = 4;
    } else if (hover) {
        weight = 3;
    }
    return {
        ...BASE_PATH_STYLE,
        color: stateStyle.color,
        fillColor: stateStyle.fillColor,
        dashArray: stateStyle.dashArray || null,
        weight,
        fillOpacity: hover ? 0.35 : BASE_PATH_STYLE.fillOpacity,
    };
};

export const getVoteErrorKind = err => {
    const status = get(err, 'response.status');
    if (status === 401 || status === 403) return 'unauthenticated';
    if (status === 409) return 'closed';
    if (status === 410) return 'retired';
    return 'error';
};
