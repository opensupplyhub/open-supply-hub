import {
    CANDIDATE_LAYER_MIN_ZOOM,
    DEFAULT_CANDIDATE_LIST_QUERY,
    applyVoteToTally,
    candidateListQueryFromSearch,
    candidateListQueryToSearch,
    formatBbox,
    formatConfidence,
    formatDistance,
    getCandidateFromFacilityPayload,
    getCandidateStyle,
    getVoteErrorKind,
    makeCandidateVotesURL,
    makeCandidatesBboxURL,
    makeCandidatesListURL,
    normalizeCandidateFeatureProperties,
    normalizeCandidateListFeature,
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

        it('treats a payload that omits voting_open as open, confirmed included', () => {
            expect(
                normalizeValidation({ state: 'confirmed', tally: {} })
                    .votingOpen,
            ).toBe(true);
            expect(
                normalizeValidation({ state: 'disputed', tally: {} })
                    .votingOpen,
            ).toBe(true);
            expect(
                normalizeValidation({ state: 'confirmed', voting_open: false })
                    .votingOpen,
            ).toBe(false);
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
    describe('list query (OSDEV-3755)', () => {
        it('parses the page URL into a query and ignores junk', () => {
            expect(
                candidateListQueryFromSearch(
                    '?page=3&sort=-nearest_m&state=disputed,bogus,confirmed' +
                        '&confidence_min=0.2&confidence_max=1.5' +
                        '&has_nearby=false&country=us&bbox=-1,-1,1,1',
                ),
            ).toEqual({
                page: 3,
                sort: '-nearest_m',
                states: ['disputed', 'confirmed'],
                confidenceMin: 0.2,
                confidenceMax: null,
                hasNearby: false,
                country: 'US',
                bbox: '-1,-1,1,1',
            });
            expect(
                candidateListQueryFromSearch('?page=0&sort=name&bbox=1,2,3'),
            ).toEqual({ ...DEFAULT_CANDIDATE_LIST_QUERY, states: [] });
            expect(candidateListQueryFromSearch('')).toEqual({
                ...DEFAULT_CANDIDATE_LIST_QUERY,
                states: [],
            });
        });

        it('round-trips through the search string, leaving defaults out', () => {
            const query = {
                ...DEFAULT_CANDIDATE_LIST_QUERY,
                page: 2,
                sort: 'confidence',
                states: ['unverified'],
                hasNearby: true,
            };
            const search = candidateListQueryToSearch(query);
            expect(search).toBe(
                '?page=2&sort=confidence&state=unverified&has_nearby=true',
            );
            expect(candidateListQueryFromSearch(search)).toEqual(query);
            expect(
                candidateListQueryToSearch(DEFAULT_CANDIDATE_LIST_QUERY),
            ).toBe('');
        });

        it('builds the API URL with the page and page size', () => {
            expect(makeCandidatesListURL(DEFAULT_CANDIDATE_LIST_QUERY)).toBe(
                '/api/v1/production-locations/candidates/?page=1&limit=50',
            );
            expect(
                makeCandidatesListURL({
                    ...DEFAULT_CANDIDATE_LIST_QUERY,
                    page: 4,
                    sort: '-nearby_count',
                    country: 'US,MX',
                    bbox: '-95,30,-76,37',
                }),
            ).toBe(
                '/api/v1/production-locations/candidates/' +
                    '?page=4&limit=50&sort=-nearby_count&country=US%2CMX' +
                    '&bbox=-95%2C30%2C-76%2C37',
            );
        });

        it('keeps a drawn-area-only request in list mode', () => {
            // `bbox` with nothing but `limit` is the legacy map call
            // (OSDEV-3249): capped at two degrees, no count, no paging.
            // The explicit `page` is what makes this a list request.
            expect(
                makeCandidatesListURL({
                    ...DEFAULT_CANDIDATE_LIST_QUERY,
                    bbox: '-95,30,-76,37',
                }),
            ).toBe(
                '/api/v1/production-locations/candidates/' +
                    '?page=1&limit=50&bbox=-95%2C30%2C-76%2C37',
            );
            // The page URL itself still leaves the default page out.
            expect(
                candidateListQueryToSearch({
                    ...DEFAULT_CANDIDATE_LIST_QUERY,
                    bbox: '-95,30,-76,37',
                }),
            ).toBe('?bbox=-95%2C30%2C-76%2C37');
        });

        it('normalizes a list feature with the list-only fields', () => {
            const row = normalizeCandidateListFeature({
                type: 'Feature',
                id: 'US2026308ABCDEF',
                properties: {
                    os_id: 'US2026308ABCDEF',
                    confidence: 0.5,
                    source: 'earth_genome',
                    state: 'disputed',
                    tally: { confirmed: 2, not_a_facility: 2 },
                    centroid: { lat: 33.7, lng: -86.9 },
                    nearby_count: 2,
                    nearest_m: 388.2,
                    nearest: {
                        os_id: 'US2025292ABCDEF',
                        name: 'Nearby',
                        distance_m: 388.2,
                    },
                    created_at: '2026-11-04T10:00:00Z',
                    country_code: 'US',
                    external_id: 'AL338',
                },
            });
            expect(row).toMatchObject({
                osId: 'US2026308ABCDEF',
                confidence: 0.5,
                externalId: 'AL338',
                createdAt: '2026-11-04T10:00:00Z',
                countryCode: 'US',
                coordinates: { lat: 33.7, lng: -86.9 },
                nearbyCount: 2,
                nearestM: 388.2,
                nearest: {
                    osId: 'US2025292ABCDEF',
                    name: 'Nearby',
                    distanceM: 388.2,
                },
                isDetailLoaded: false,
            });
            expect(row.validation.state).toBe(CANDIDATE_STATES.DISPUTED);
            expect(row.validation.tally).toEqual({
                confirmed: 2,
                not_a_facility: 2,
            });

            const alone = normalizeCandidateListFeature({
                properties: {
                    os_id: 'US2026308AAAAAA',
                    nearby_count: 0,
                    nearest_m: null,
                    nearest: null,
                },
            });
            expect(alone.nearbyCount).toBe(0);
            expect(alone.nearestM).toBeNull();
            expect(alone.nearest).toBeNull();
            expect(normalizeCandidateListFeature({ properties: {} })).toBeNull();
        });
    });
});
