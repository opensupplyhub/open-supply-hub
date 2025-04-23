import React from 'react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityDetailsGeneralFields from '../../components/FacilityDetailsGeneralFields';

describe('FacilityDetailsGeneralFields component: test rendering of additional identifiers', () => {
    const mockData = {
        id: 'US202510850SQCV',
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [-73.8314318, 40.762569],
        },
        properties: {
            name: 'Nice production location LTD',
            country_code: 'US',
            os_id: 'US202510850SQCV',
            other_names: [],
            contributors: [
                {
                    id: 1139,
                    name: 'Test Org (Test list)',
                    is_verified: false,
                    contributor_name: 'Test Org',
                    list_name: 'Test list',
                },
            ],
            country_name: 'United States',
            claim_info: null,
            other_locations: [],
            is_closed: null,
            activity_reports: [],
            contributor_fields: [],
            new_os_id: null,
            has_inexact_coordinates: false,
            extended_fields: {
                name: [
                    {
                        value: 'Nice production location LTD',
                        field_name: 'name',
                        contributor_id: 1139,
                        contributor_name: 'Test Org',
                        updated_at: '2025-04-18T11:25:32.798875Z',
                        created_at: '2025-04-18T11:21:15.877648Z',
                    },
                ],
                number_of_workers: [],
                native_language_name: [],
                facility_type: [],
                processing_type: [],
                product_type: [],
                parent_company: [
                    {
                        id: 3394113,
                        is_verified: false,
                        value: {
                            name: 'Moon company',
                            raw_value: 'Moon company',
                        },
                        created_at: '2025-04-18T11:21:15.940646Z',
                        updated_at: '2025-04-18T11:25:32.885850Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'parent_company',
                        verified_count: 0,
                    },
                ],
                duns_id: [
                    {
                        id: 83087,
                        is_verified: false,
                        value: {
                            raw_value: 2120383532,
                        },
                        created_at: '2022-04-01T10:49:15.174025Z',
                        updated_at: '2022-04-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'duns_id',
                        verified_count: 0,
                    },
                ],
                lei_id: [
                    {
                        id: 83087,
                        is_verified: false,
                        value: {
                            raw_value: '529900T8BM49AURSDO55',
                        },
                        created_at: '2022-04-01T10:49:15.174025Z',
                        updated_at: '2022-04-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'lei_id',
                        verified_count: 0,
                    },
                ],
                rba_id: [
                    {
                        id: 83087,
                        is_verified: false,
                        value: {
                            raw_value:
                                'F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E',
                        },
                        created_at: '2022-04-01T10:49:15.174025Z',
                        updated_at: '2022-04-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'rba_id',
                        verified_count: 0,
                    },
                ],
            },
            created_from: {
                created_at: '2025-04-18T11:21:15.877648Z',
                contributor: 'Test Org',
            },
            sector: [
                {
                    updated_at: '2025-04-18T11:25:32.798875Z',
                    contributor_id: 1139,
                    contributor_name: 'Test Org',
                    values: ['Unspecified'],
                    is_from_claim: false,
                    created_at: '2025-04-18T11:21:15.877648Z',
                },
            ],
            is_claimed: false,
        },
    };

    const handleFormat = ({ value, formatValue }) => ({
        primary: formatValue(value),
    });

    const defaultProps = {
        data: mockData,
        nameField: { primary: 'Nice production location LTD' },
        otherNames: [],
        embed: false,
        embedConfig: {},
        formatExtendedField: handleFormat,
        formatIfListAndRemoveDuplicates: jest.fn(),
        hideSectorData: false,
        isClaimed: false,
    };

    test('renders only non-additional identifier extended fields when the show_additional_identifiers feature flag is false', () => {
        const preloadedState = {
            featureFlags: {
                fetching: false,
                flags: {
                    show_additional_identifiers: false,
                },
            },
        };
        const {
            getByText,
            queryByText,
        } = renderWithProviders(
            <FacilityDetailsGeneralFields {...defaultProps} />,
            { preloadedState },
        );

        expect(getByText('Name')).toBeInTheDocument();
        expect(getByText('Nice production location LTD')).toBeInTheDocument();
        expect(getByText('Parent Company')).toBeInTheDocument();
        expect(getByText('Moon company')).toBeInTheDocument();

        expect(queryByText('LEI ID')).not.toBeInTheDocument();
        expect(queryByText('RBA ID')).not.toBeInTheDocument();
        expect(queryByText('DUNS ID')).not.toBeInTheDocument();
    });

    test('renders all extended fields when the show_additional_identifiers feature flag is true', () => {
        const preloadedState = {
            featureFlags: {
                fetching: false,
                flags: {
                    show_additional_identifiers: true,
                },
            },
        };
        const { getByText } = renderWithProviders(
            <FacilityDetailsGeneralFields {...defaultProps} />,
            { preloadedState },
        );

        expect(getByText('Name')).toBeInTheDocument();
        expect(getByText('Nice production location LTD')).toBeInTheDocument();
        expect(getByText('Parent Company')).toBeInTheDocument();
        expect(getByText('Moon company')).toBeInTheDocument();

        expect(getByText('LEI ID')).toBeInTheDocument();
        expect(getByText('529900T8BM49AURSDO55')).toBeInTheDocument();
        expect(getByText('RBA ID')).toBeInTheDocument();
        expect(
            getByText(
                'F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E1F342E6157BD84B70AB40BF9A6C0C19E',
            ),
        ).toBeInTheDocument();
        expect(getByText('DUNS ID')).toBeInTheDocument();
        expect(getByText('2120383532')).toBeInTheDocument();
    });
});
