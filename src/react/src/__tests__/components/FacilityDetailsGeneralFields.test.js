import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityDetailsGeneralFields from '../../components/FacilityDetailsGeneralFields';

describe('FacilityDetailsGeneralFields component', () => {
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
                parent_company_os_id: [
                    {
                        id: 83088,
                        is_verified: false,
                        value: {
                            raw_values: [
                                'US202510850SQCV',
                                'US202511345DVTE',
                            ],
                        },
                        created_at: '2025-05-01T10:49:15.174025Z',
                        updated_at: '2025-05-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'parent_company_os_id',
                        verified_count: 0,
                    },
                    {
                        id: 83089,
                        is_verified: false,
                        value: {
                            raw_values: [
                                'BD2025108DNTPFS',
                                'CN202510809MKXG',
                            ],
                        },
                        created_at: '2025-05-01T10:49:15.174025Z',
                        updated_at: '2025-05-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'parent_company_os_id',
                        verified_count: 0,
                    }
                ],
                isic_4: [
                    {
                        id: 83090,
                        is_verified: false,
                        value: {
                            section: 'J - Information and communication',
                            division:
                                '62 - Computer programming, consultancy and related activities',
                            group:
                                '62 - Computer programming, consultancy and related activities',
                            class:
                                '620 - Computer programming, consultancy and related activities',
                        },
                        created_at: '2025-05-01T10:49:15.174025Z',
                        updated_at: '2025-05-01T10:58:25.043413Z',
                        contributor_name: 'Test Org',
                        contributor_id: 1139,
                        value_count: 1,
                        is_from_claim: false,
                        field_name: 'isic_4',
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

    const defaultProps = {
        data: mockData,
        nameField: { primary: 'Nice production location LTD' },
        otherNames: [],
        embed: false,
        embedConfig: {},
        hideSectorData: false,
        isClaimed: false,
    };


    const renderComponent = (props = {}, preloadedState = {}) =>
        renderWithProviders(
            <MemoryRouter>
                <FacilityDetailsGeneralFields {...defaultProps} {...props} />
            </MemoryRouter>,
            { preloadedState },
        );

    test('renders ISIC 4 without divider when single block in contribution', () => {
        const { queryByText, queryAllByRole } = renderComponent();

        expect(
            queryByText('Section: J - Information and communication'),
        ).toBeInTheDocument();
        expect(
            queryByText(
                'Division: 62 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();
        expect(
            queryByText(
                'Group: 62 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();
        expect(
            queryByText(
                'Class: 620 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();

        const dividers = queryAllByRole('separator');
        expect(dividers.length).toBe(0);
    });

    test('renders ISIC 4 with divider between multiple blocks in same contribution', () => {
        const multiIsicData = {
            ...mockData,
            properties: {
                ...mockData.properties,
                extended_fields: {
                    ...mockData.properties.extended_fields,
                    isic_4: [
                        {
                            id: 90001,
                            is_verified: false,
                            value: {
                                raw_value: [
                                    {
                                        section:
                                            'J - Information and communication',
                                        division:
                                            '62 - Computer programming, consultancy and related activities',
                                        group:
                                            '62 - Computer programming, consultancy and related activities',
                                        class:
                                            '620 - Computer programming, consultancy and related activities',
                                    },
                                    {
                                        section:
                                            'G - Wholesale and retail trade; repair of motor vehicles and motorcycles',
                                        division:
                                            '47 - Retail trade, except motor vehicles and motorcycles',
                                        group:
                                            '47 - Retail trade, except motor vehicles and motorcycles',
                                        class:
                                            '471 - Retail sale in non-specialized stores with food, beverages or tobacco predominating',
                                    },
                                ],
                            },
                            created_at: '2025-05-01T10:49:15.174025Z',
                            updated_at: '2025-05-01T10:58:25.043413Z',
                            contributor_name: 'Test Org',
                            contributor_id: 1139,
                            value_count: 1,
                            is_from_claim: false,
                            field_name: 'isic_4',
                            verified_count: 0,
                        },
                    ],
                },
            },
        };

        const { getAllByRole, getByText } = renderComponent({
            data: multiIsicData,
        });

        expect(
            getByText('Section: J - Information and communication'),
        ).toBeInTheDocument();
        expect(
            getByText(
                'Section: G - Wholesale and retail trade; repair of motor vehicles and motorcycles',
            ),
        ).toBeInTheDocument();

        const dividers = getAllByRole('separator');
        expect(dividers.length).toBeGreaterThanOrEqual(1);
    });

    test('deduplicates repeated ISIC 4 entries from the same contribution', () => {
        const duplicateIsicData = {
            ...mockData,
            properties: {
                ...mockData.properties,
                extended_fields: {
                    ...mockData.properties.extended_fields,
                    isic_4: [
                        {
                            id: 90002,
                            is_verified: false,
                            value: {
                                raw_value: [
                                    {
                                        section:
                                            'J - Information and communication',
                                        division:
                                            '62 - Computer programming, consultancy and related activities',
                                        group:
                                            '62 - Computer programming, consultancy and related activities',
                                        class:
                                            '620 - Computer programming, consultancy and related activities',
                                    },
                                    {
                                        section:
                                            'J - Information and communication',
                                        division:
                                            '62 - Computer programming, consultancy and related activities',
                                        group:
                                            '62 - Computer programming, consultancy and related activities',
                                        class:
                                            '620 - Computer programming, consultancy and related activities',
                                    },
                                    {
                                        section:
                                            'G - Wholesale and retail trade; repair of motor vehicles and motorcycles',
                                        division:
                                            '47 - Retail trade, except motor vehicles and motorcycles',
                                        group:
                                            '47 - Retail trade, except motor vehicles and motorcycles',
                                        class:
                                            '471 - Retail sale in non-specialized stores with food, beverages or tobacco predominating',
                                    },
                                ],
                            },
                            created_at: '2025-05-01T10:49:15.174025Z',
                            updated_at: '2025-05-01T10:58:25.043413Z',
                            contributor_name: 'Test Org',
                            contributor_id: 1139,
                            value_count: 1,
                            is_from_claim: false,
                            field_name: 'isic_4',
                            verified_count: 0,
                        },
                    ],
                },
            },
        };

        const { getAllByRole, getAllByText } = renderComponent({
            data: duplicateIsicData,
        });

        expect(
            getAllByText('Section: J - Information and communication').length,
        ).toBe(1);
        expect(
            getAllByText(
                'Section: G - Wholesale and retail trade; repair of motor vehicles and motorcycles',
            ).length,
        ).toBe(1);
        expect(getAllByRole('separator').length).toBe(1);
    });

    test('renders only non-additional identifier extended fields when the show_additional_identifiers feature flag is false', () => {
        const preloadedState = {
            featureFlags: {
                fetching: false,
                flags: {
                    show_additional_identifiers: false,
                },
            },
        };

        const { getByText, queryByText} = renderComponent({}, preloadedState);

        expect(getByText('Name')).toBeInTheDocument();
        expect(getByText('Nice production location LTD')).toBeInTheDocument();
        expect(getByText('Parent Company')).toBeInTheDocument();
        expect(getByText('Moon company')).toBeInTheDocument();
        expect(getByText('Parent Company OS ID')).toBeInTheDocument();
        expect(getByText('US202510850SQCV')).toBeInTheDocument();
        expect(getByText('US202511345DVTE')).toBeInTheDocument();

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
        
        const { getByText} = renderComponent({}, preloadedState);

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

    test('renders parent company os id with multiple values', () => {
        const { getByText, queryByText } = renderComponent();
        
        expect(getByText('Parent Company OS ID')).toBeInTheDocument();
        expect(getByText('US202510850SQCV')).toBeInTheDocument();
        expect(getByText('US202511345DVTE')).toBeInTheDocument();
        const firstParentOsIdLink = getByText('US202510850SQCV');
        expect(firstParentOsIdLink.closest('a')).toHaveAttribute(
            'href',
            '/facilities/US202510850SQCV',
        );
        const secondParentOsIdLink = getByText('US202511345DVTE');
        expect(secondParentOsIdLink.closest('a')).toHaveAttribute(
            'href',
            '/facilities/US202511345DVTE',
        );
        expect(queryByText('BD2025108DNTPFS')).not.toBeInTheDocument();
        expect(queryByText('CN202510809MKXG')).not.toBeInTheDocument();
        expect(queryByText('1 more entry')).toBeInTheDocument();
    });

    test('renders parent company os id with multiple values and shows more entries', () => {
        const { getByText } = renderComponent();

        const getMoreEntriesButton = getByText('1 more entry');
        expect(getMoreEntriesButton).toBeInTheDocument();
        getMoreEntriesButton.click();
        expect(getByText('BD2025108DNTPFS')).toBeInTheDocument();
        expect(getByText('CN202510809MKXG')).toBeInTheDocument();
        const firstParentOsIdLink = getByText('BD2025108DNTPFS');
        expect(firstParentOsIdLink.closest('a')).toHaveAttribute(
            'href',
            '/facilities/BD2025108DNTPFS',
        );
        const secondParentOsIdLink = getByText('CN202510809MKXG');
        expect(secondParentOsIdLink.closest('a')).toHaveAttribute(
            'href',
            '/facilities/CN202510809MKXG',
        );
    });

    test('renders sector data when hideSectorData is false', () => {
        const { getByText } = renderComponent();

        expect(getByText('Sector')).toBeInTheDocument();
        expect(getByText('Unspecified')).toBeInTheDocument();
    });

    test('does not render sector data when hideSectorData is true', () => {
        const { queryByText } = renderComponent({
            hideSectorData: true,
        });

        expect(queryByText('Sector')).not.toBeInTheDocument();
    });

    test('renders the name field correctly', () => {
        const { getByText } = renderComponent();

        expect(getByText('Name')).toBeInTheDocument();
        expect(getByText('Nice production location LTD')).toBeInTheDocument();
    });

    test('renders ISIC 4 field with formatted section, division, group, and class', () => {
        const { getByText } = renderComponent();

        expect(getByText('ISIC 4')).toBeInTheDocument();
        expect(
            getByText('Section: J - Information and communication'),
        ).toBeInTheDocument();
        expect(
            getByText(
                'Division: 62 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();
        expect(
            getByText(
                'Group: 62 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();
        expect(
            getByText(
                'Class: 620 - Computer programming, consultancy and related activities',
            ),
        ).toBeInTheDocument();
    });

    test('does not render ISIC 4 section when object contains no valid ISIC-4 fields', () => {
        const dataWithInvalidIsic4 = {
            ...mockData,
            properties: {
                ...mockData.properties,
                extended_fields: {
                    ...mockData.properties.extended_fields,
                    isic_4: [
                        {
                            id: 83091,
                            is_verified: false,
                            value: {
                                invalid_field_1: 'some value',
                                invalid_field_2: 'another value',
                            },
                            created_at: '2025-05-01T10:49:15.174025Z',
                            updated_at: '2025-05-01T10:58:25.043413Z',
                            contributor_name: 'Test Org',
                            contributor_id: 1139,
                            value_count: 1,
                            is_from_claim: false,
                            field_name: 'isic_4',
                            verified_count: 0,
                        },
                    ],
                },
            },
        };

        const { queryByText } = renderComponent({ data: dataWithInvalidIsic4 });

        expect(queryByText('ISIC 4')).not.toBeInTheDocument();
    });

    test('does not render ISIC 4 section when all ISIC-4 fields are empty', () => {
        const dataWithEmptyIsic4 = {
            ...mockData,
            properties: {
                ...mockData.properties,
                extended_fields: {
                    ...mockData.properties.extended_fields,
                    isic_4: [
                        {
                            id: 83092,
                            is_verified: false,
                            value: {
                                section: '',
                                division: '',
                                group: '',
                                class: '',
                            },
                            created_at: '2025-05-01T10:49:15.174025Z',
                            updated_at: '2025-05-01T10:58:25.043413Z',
                            contributor_name: 'Test Org',
                            contributor_id: 1139,
                            value_count: 1,
                            is_from_claim: false,
                            field_name: 'isic_4',
                            verified_count: 0,
                        },
                    ],
                },
            },
        };

        const { queryByText } = renderComponent({ data: dataWithEmptyIsic4 });

        expect(queryByText('ISIC 4')).not.toBeInTheDocument();
    });

    test('does not render facility type when matched value is null (skipped matching)', () => {
        const dataWithNullMatchedFacilityType = {
            ...mockData,
            properties: {
                ...mockData.properties,
                extended_fields: {
                    ...mockData.properties.extended_fields,
                    facility_type: [
                        {
                            id: 3992815,
                            is_verified: false,
                            value: {
                                raw_values: 'Manufacturer',
                                matched_values: [
                                    [
                                        'PROCESSING_TYPE',
                                        'SKIPPED_MATCHING',
                                        null,
                                        'Manufacturer',
                                    ],
                                ],
                            },
                            updated_at: '2025-07-28T03:50:18.988790Z',
                            contributor_name: 'Tchibo',
                            contributor_id: 3314,
                            value_count: 5,
                            is_from_claim: false,
                            field_name: 'facility_type',
                            verified_count: 0,
                            source_by: null,
                            unit: null,
                            label: null,
                            base_url: null,
                            display_text: null,
                            json_schema: null,
                        },
                    ],
                },
            },
        };

        const { queryByText } = renderComponent({
            data: dataWithNullMatchedFacilityType,
        });

        expect(queryByText('Facility Type')).not.toBeInTheDocument();
    });
});
