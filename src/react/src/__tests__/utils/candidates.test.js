import {
    CANDIDATE_LAYER_MIN_ZOOM,
    applyVoteToTally,
    formatBbox,
    formatConfidence,
    formatDistance,
    getCandidateFromFacilityPayload,
    getCandidateStyle,
    getVoteErrorKind,
    makeCandidateVotesURL,
    makeCandidatesBboxURL,
    normalizeCandidateFeatureProperties,
    normalizeValidation,
    shouldFetchCandidates,
} from '../../util/candidates';
import { CANDIDATE_STATES } from '../../util/candidateCopy';

const bounds = {
    getWest: () => -79.1234567,
    getSouth: () => 35.1,
    getEast: () => -79.1,
    getNorth: () => 35.2000004,
};

describe('candidates util', () => {
    describe('bbox request building', () => {
        it('formats bounds as minLng,minLat,maxLng,maxLat rounded to 6 dp', () => {
            expect(formatBbox(bounds)).toBe('-79.123457,35.1,-79.1,35.2');
        });

        it('builds the candidates URL with bbox and limit', () => {
            expect(makeCandidatesBboxURL(formatBbox(bounds))).toBe(
                '/api/v1/production-locations/candidates/?bbox=-79.123457,35.1,-79.1,35.2&limit=200',
            );
            expect(makeCandidatesBboxURL('1,2,3,4', 50)).toBe(
                '/api/v1/production-locations/candidates/?bbox=1,2,3,4&limit=50',
            );
        });

        it('only fetches at or above the minimum zoom', () => {
            expect(shouldFetchCandidates(CANDIDATE_LAYER_MIN_ZOOM - 1)).toBe(
                false,
            );
            expect(shouldFetchCandidates(CANDIDATE_LAYER_MIN_ZOOM)).toBe(true);
            expect(shouldFetchCandidates(18)).toBe(true);
            expect(shouldFetchCandidates(undefined)).toBe(false);
        });

        it('builds the votes URL for an OS ID', () => {
            expect(makeCandidateVotesURL('US2026ABC')).toBe(
                '/api/v1/production-locations/US2026ABC/candidate-votes/',
            );
        });
    });

    describe('normalizeValidation', () => {
        it('defaults to unverified, zero tally and open voting', () => {
            expect(normalizeValidation(undefined)).toEqual({
                state: 'unverified',
                tally: { confirmed: 0, not_a_facility: 0 },
                yourVote: undefined,
                votingOpen: true,
            });
        });

        it('derives voting_open from state when the payload omits it', () => {
            expect(
                normalizeValidation({ state: 'confirmed', tally: {} })
                    .votingOpen,
            ).toBe(false);
            expect(
                normalizeValidation({ state: 'disputed', tally: {} })
                    .votingOpen,
            ).toBe(true);
        });

        it('keeps an explicit voting_open and your_vote', () => {
            expect(
                normalizeValidation({
                    state: 'unverified',
                    tally: { confirmed: 1 },
                    your_vote: null,
                    voting_open: true,
                }),
            ).toEqual({
                state: 'unverified',
                tally: { confirmed: 1, not_a_facility: 0 },
                yourVote: null,
                votingOpen: true,
            });
        });
    });

    describe('normalizeCandidateFeatureProperties', () => {
        it('maps a bbox feature to a partial candidate', () => {
            const candidate = normalizeCandidateFeatureProperties({
                os_id: 'US2026ABC',
                confidence: 0.87,
                source: 'Earth Genome',
                state: 'disputed',
                tally: { confirmed: 3, not_a_facility: 2 },
                centroid: { lat: 35.1, lng: -79.1 },
            });
            expect(candidate).toMatchObject({
                osId: 'US2026ABC',
                confidence: 0.87,
                source: 'Earth Genome',
                coordinates: { lat: 35.1, lng: -79.1 },
                isDetailLoaded: false,
                validation: {
                    state: 'disputed',
                    tally: { confirmed: 3, not_a_facility: 2 },
                    votingOpen: true,
                },
            });
            expect(candidate.validation.yourVote).toBeUndefined();
        });

        it('returns null without an os_id', () => {
            expect(normalizeCandidateFeatureProperties({})).toBeNull();
            expect(normalizeCandidateFeatureProperties(null)).toBeNull();
        });
    });

    describe('getCandidateFromFacilityPayload', () => {
        it('returns null for a confirmed facility', () => {
            expect(
                getCandidateFromFacilityPayload({
                    properties: { name: 'Mill', is_candidate: false },
                }),
            ).toBeNull();
            expect(getCandidateFromFacilityPayload(null)).toBeNull();
        });

        it('maps the legacy feature candidate block', () => {
            const candidate = getCandidateFromFacilityPayload({
                id: 'US2026ABC',
                geometry: { type: 'Point', coordinates: [-79.1, 35.1] },
                properties: {
                    os_id: 'US2026ABC',
                    name: '',
                    is_candidate: true,
                    country_name: 'United States',
                    candidate: {
                        source: 'Earth Genome',
                        confidence: 0.91,
                        external_id: 'eg-1',
                        validation: {
                            state: 'unverified',
                            tally: { confirmed: 1, not_a_facility: 0 },
                            your_vote: 'confirmed',
                            voting_open: true,
                        },
                        suggested_matches: [
                            {
                                os_id: 'US2020XYZ',
                                name: 'Nearby Farm',
                                address: '1 Farm Rd',
                                distance_m: 240.4,
                            },
                            { name: 'missing os id' },
                        ],
                    },
                },
            });
            expect(candidate).toEqual({
                osId: 'US2026ABC',
                source: 'Earth Genome',
                confidence: 0.91,
                externalId: 'eg-1',
                createdAt: null,
                coordinates: { lat: 35.1, lng: -79.1 },
                countryName: 'United States',
                validation: {
                    state: 'unverified',
                    tally: { confirmed: 1, not_a_facility: 0 },
                    yourVote: 'confirmed',
                    votingOpen: true,
                },
                suggestedMatches: [
                    {
                        osId: 'US2020XYZ',
                        name: 'Nearby Farm',
                        address: '1 Farm Rd',
                        distanceM: 240.4,
                    },
                ],
                isDetailLoaded: true,
            });
        });
    });

    describe('getCandidateFromFacilityPayload backend contract', () => {
        // Verbatim shape of the legacy GET /api/facilities/{os_id}/ Feature
        // for a candidate, as built by FacilityCandidateDetailsSerializer in
        // src/django/api/serializers/facility/
        // facility_candidate_details_serializer.py (OSDEV-3249, shared
        // contract: `properties.candidate` with `validation` nested and
        // `created_at`). Only `extended_fields` is abbreviated.
        const backendFeature = {
            id: 'US2026ABCDEF1234',
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [-79.1, 35.1] },
            properties: {
                name: '',
                address: '',
                country_code: 'US',
                country_name: 'United States',
                os_id: 'US2026ABCDEF1234',
                is_candidate: true,
                candidate: {
                    source: 'Earth Genome',
                    external_id: 'eg-42',
                    confidence: 0.91,
                    polygon: {
                        type: 'Polygon',
                        coordinates: [
                            [
                                [-79.11, 35.09],
                                [-79.09, 35.09],
                                [-79.09, 35.11],
                                [-79.11, 35.11],
                                [-79.11, 35.09],
                            ],
                        ],
                    },
                    suggested_matches: [
                        {
                            os_id: 'US2020XYZ',
                            name: 'Nearby Farm',
                            address: '1 Farm Rd',
                            distance_m: 240.4,
                        },
                    ],
                    created_at: '2026-09-01T00:00:00Z',
                    validation: {
                        state: 'disputed',
                        tally: { confirmed: 2, not_a_facility: 1 },
                        your_vote: 'confirmed',
                        voting_open: true,
                    },
                },
                other_names: [],
                other_addresses: [],
                contributors: [],
                claim_info: null,
                other_locations: [],
                is_closed: null,
                activity_reports: [],
                contributor_fields: [],
                new_os_id: null,
                has_inexact_coordinates: false,
                extended_fields: { name: [], address: [] },
                created_from: {
                    created_at: '2026-09-01T00:00:00Z',
                    contributor: 'Earth Genome',
                },
                sector: [],
                is_claimed: false,
                partner_fields: {},
                is_data_center: false,
            },
        };

        it('reads the nested validation block and created_at', () => {
            const candidate = getCandidateFromFacilityPayload(backendFeature);
            expect(candidate.validation).toEqual({
                state: 'disputed',
                tally: { confirmed: 2, not_a_facility: 1 },
                yourVote: 'confirmed',
                votingOpen: true,
            });
            expect(candidate.createdAt).toBe('2026-09-01T00:00:00Z');
            expect(candidate.osId).toBe('US2026ABCDEF1234');
            expect(candidate.source).toBe('Earth Genome');
            expect(candidate.confidence).toBe(0.91);
            expect(candidate.externalId).toBe('eg-42');
            expect(candidate.countryName).toBe('United States');
            expect(candidate.suggestedMatches).toHaveLength(1);
            expect(candidate.isDetailLoaded).toBe(true);
        });

        it('falls back to flat validation keys and created_from.created_at', () => {
            const { validation, ...rest } = backendFeature.properties.candidate;
            const flat = {
                ...backendFeature,
                properties: {
                    ...backendFeature.properties,
                    candidate: { ...rest, ...validation, created_at: undefined },
                },
            };
            const candidate = getCandidateFromFacilityPayload(flat);
            expect(candidate.validation).toEqual({
                state: 'disputed',
                tally: { confirmed: 2, not_a_facility: 1 },
                yourVote: 'confirmed',
                votingOpen: true,
            });
            expect(candidate.createdAt).toBe('2026-09-01T00:00:00Z');
        });
    });

    describe('applyVoteToTally', () => {
        it('adds a first vote', () => {
            expect(
                applyVoteToTally(
                    { confirmed: 2, not_a_facility: 1 },
                    null,
                    'not_a_facility',
                ),
            ).toEqual({ confirmed: 2, not_a_facility: 2 });
        });

        it('moves a changed vote between buckets', () => {
            expect(
                applyVoteToTally(
                    { confirmed: 2, not_a_facility: 1 },
                    'confirmed',
                    'not_a_facility',
                ),
            ).toEqual({ confirmed: 1, not_a_facility: 2 });
        });

        it('is a no-op for the same vote', () => {
            expect(
                applyVoteToTally(
                    { confirmed: 2, not_a_facility: 1 },
                    'confirmed',
                    'confirmed',
                ),
            ).toEqual({ confirmed: 2, not_a_facility: 1 });
        });
    });

    describe('styling', () => {
        it('uses a dashed outline for unverified and solid for confirmed', () => {
            expect(
                getCandidateStyle(CANDIDATE_STATES.UNVERIFIED).dashArray,
            ).toBe('6 4');
            expect(
                getCandidateStyle(CANDIDATE_STATES.CONFIRMED).dashArray,
            ).toBeNull();
            expect(
                getCandidateStyle(CANDIDATE_STATES.DISPUTED).color,
            ).toEqual(
                getCandidateStyle(CANDIDATE_STATES.RETIREMENT_PENDING).color,
            );
        });

        it('thickens hovered and selected features', () => {
            expect(getCandidateStyle('unverified').weight).toBe(2);
            expect(getCandidateStyle('unverified', { hover: true }).weight).toBe(
                3,
            );
            expect(
                getCandidateStyle('unverified', { selected: true }).weight,
            ).toBe(4);
        });

        it('falls back to unverified for unknown states', () => {
            expect(getCandidateStyle('nope')).toEqual(
                getCandidateStyle('unverified'),
            );
        });
    });

    describe('formatting and errors', () => {
        it('formats confidence and distance', () => {
            expect(formatConfidence(0.874)).toBe('87%');
            expect(formatConfidence(null)).toBe('—');
            expect(formatDistance(240.4)).toBe('240 m');
            expect(formatDistance(1540)).toBe('1.5 km');
            expect(formatDistance(null)).toBe('');
        });

        it('classifies vote errors by status', () => {
            expect(getVoteErrorKind({ response: { status: 401 } })).toBe(
                'unauthenticated',
            );
            expect(getVoteErrorKind({ response: { status: 403 } })).toBe(
                'unauthenticated',
            );
            expect(getVoteErrorKind({ response: { status: 409 } })).toBe(
                'closed',
            );
            expect(getVoteErrorKind({ response: { status: 410 } })).toBe(
                'retired',
            );
            expect(getVoteErrorKind(new Error('network'))).toBe('error');
        });
    });
});
