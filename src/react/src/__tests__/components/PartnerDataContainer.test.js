import React from 'react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerDataContainer from '../../components/ProductionLocation/PartnerSection/PartnerDataContainer/PartnerDataContainer';

const makePartnerFieldEntry = (fieldName, value) => ({
    value,
    created_at: '2025-06-01T00:00:00Z',
    contributor_name: 'Test Partner',
    contributor_id: 1,
    is_from_claim: false,
    is_verified: false,
    field_name: fieldName,
    label: null,
    source_by: null,
});

const makeGroup = (fieldNames, overrides = {}) => ({
    uuid: 'group-1',
    name: 'Test Group',
    icon_file: null,
    helper_text: '<p>Helper</p>',
    description: '',
    partner_fields: fieldNames,
    ...overrides,
});

const buildState = (facilityData, groups = [], fetching = false) => ({
    facilities: { singleFacility: { data: facilityData } },
    partnerFieldGroups: {
        data: { results: groups },
        fetching,
    },
    sectionNavigation: {
        scrollTargetId: null,
        openSectionIds: {},
    },
});

describe('PartnerDataContainer component', () => {
    test('renders nothing when facilityData is null', () => {
        const state = buildState(null, [makeGroup(['climate_trace'])]);
        const { container } = renderWithProviders(
            <PartnerDataContainer />,
            { preloadedState: state },
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders nothing when facilityData has no partner_fields property', () => {
        const facilityData = { properties: {} };
        const state = buildState(facilityData, [makeGroup(['climate_trace'])]);
        const { container } = renderWithProviders(
            <PartnerDataContainer />,
            { preloadedState: state },
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders nothing when all partner_fields have empty arrays', () => {
        const facilityData = {
            properties: { partner_fields: { climate_trace: [] } },
        };
        const state = buildState(facilityData, [makeGroup(['climate_trace'])]);
        const { container } = renderWithProviders(
            <PartnerDataContainer />,
            { preloadedState: state },
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders nothing when partner_fields first entry is falsy', () => {
        const facilityData = {
            properties: { partner_fields: { climate_trace: [null] } },
        };
        const state = buildState(facilityData, [makeGroup(['climate_trace'])]);
        const { container } = renderWithProviders(
            <PartnerDataContainer />,
            { preloadedState: state },
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders the section when facilityData has valid partner field values', () => {
        const facilityData = {
            properties: {
                partner_fields: {
                    climate_trace: [
                        makePartnerFieldEntry('climate_trace', 'CO2: 500t'),
                    ],
                },
            },
        };
        const state = buildState(facilityData, [makeGroup(['climate_trace'])]);
        const { getByText } = renderWithProviders(
            <PartnerDataContainer />,
            { preloadedState: state },
        );
        expect(getByText('Partner Data')).toBeInTheDocument();
    });
});
