import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimedFacilitiesDetails from '../../components/ClaimedFacilitiesDetails/ClaimedFacilitiesDetails';

jest.mock('react-redux', () => {
    const actual = jest.requireActual('react-redux');
    return {
        ...actual,
        connect: () => Component => Component,
    };
});

beforeAll(() => {
    jest.spyOn(React, 'useEffect').mockImplementation(() => {});
});

jest.mock('../../components/InputSection', () => props => (
    <div data-testid={`input-${props.label}`}>{props.label}</div>
));

// Mock sidebar to avoid facilityDetails shape requirements in this test.
jest.mock('../../components/ClaimedFacilitiesDetailsSidebar', () => () => (
    <div data-testid="claimed-sidebar" />
));

jest.mock('../../actions/claimedFacilityDetails', () => {
    const actual = jest.requireActual('../../actions/claimedFacilityDetails');
    return {
        __esModule: true,
        ...actual,
        fetchClaimedFacilityDetails: jest.fn(() => () => ({
            type: 'FETCH_CLAIMED',
        })),
        clearClaimedFacilityDetails: jest.fn(() => ({ type: 'CLEAR_CLAIMED' })),
        submitClaimedFacilityDetailsUpdate: jest.fn(() => ({
            type: 'SUBMIT_CLAIMED',
        })),
    };
});

jest.mock('../../actions/filterOptions', () => {
    const actual = jest.requireActual('../../actions/filterOptions');
    return {
        ...actual,
        fetchSectorOptions: jest.fn(() => () => null),
    };
});

const baseClaimData = {
    facility_name_native_language: 'Название',
    facility_name_english: 'Mock Facility',
    sector: ['Apparel'],
    facility_phone_number: '+1-555-0000',
    facility_phone_number_publicly_visible: true,
    facility_website: 'https://example.com',
    facility_website_publicly_visible: true,
    facility_description: 'Mock description',
    facility_address: '123 Test St',
    facility_parent_company: { id: 42, name: 'Parent Co' },
    parent_company_name: 'Parent Co',
    facility_minimum_order_quantity: '500 pcs',
    facility_average_lead_time: '15 days',
    facility_workers_count: '100-200',
    facility_female_workers_percentage: '55',
    facility_affiliations: ['Sustainable Apparel Coalition'],
    facility_certifications: ['BCI'],
    facility_production_types: ['Cutting'],
    facility_product_types: ['Shirts'],
    point_of_contact_publicly_visible: true,
    point_of_contact_person_name: 'POC Name',
    point_of_contact_email: 'poc@example.com',
    office_info_publicly_visible: true,
    office_official_name: 'HQ Office',
    office_address: '456 Office Rd',
    office_country_code: 'US',
    office_phone_number: '+1-555-1111',
    countries: [['US', 'United States']],
    affiliation_choices: [],
    certification_choices: [],
    production_type_choices: [],
    opening_date: '2020',
    closing_date: '2021-12',
    estimated_annual_throughput: '123456',
    energy_coal: '10',
    energy_natural_gas: '20',
    energy_diesel: '30',
    energy_kerosene: '40',
    energy_biomass: '50',
    energy_charcoal: '60',
    energy_animal_waste: '70',
    energy_electricity: '80',
    energy_other: '90',
    facility: {
        id: 'fac-1',
        type: 'Feature',
        geometry: {},
        properties: {
            name: 'Test Facility',
        },
    },
    id: 1,
};

const preloadedState = {
    claimedFacilityDetails: {
        data: baseClaimData,
        retrieveData: { fetching: false, error: null },
        updateData: { fetching: false, error: null },
    },
    filterOptions: {
        sectors: { data: [], fetching: false, error: null },
    },
    auth: {
        user: {
            user: {
                isAnon: false,
                is_superuser: false,
                is_staff: false,
                is_moderation_mode: false,
                allowed_records_number: 0,
            },
        },
    },
};

const renderComponent = () =>
    renderWithProviders(
        <ClaimedFacilitiesDetails
            match={{ params: { claimID: '123' } }}
            user={preloadedState.auth.user.user}
            fetching={false}
            errors={null}
            data={baseClaimData}
            getDetails={jest.fn()}
            clearDetails={jest.fn()}
            updateFacilityNameNativeLanguage={jest.fn()}
            updateFacilityLocation={jest.fn()}
            updateSector={jest.fn()}
            updateFacilityPhone={jest.fn()}
            updateFacilityWebsite={jest.fn()}
            updateFacilityWebsiteVisibility={jest.fn()}
            updateFacilityDescription={jest.fn()}
            updateFacilityMinimumOrder={jest.fn()}
            updateFacilityAverageLeadTime={jest.fn()}
            updateFacilityWorkersCount={jest.fn()}
            updateFacilityFemaleWorkersPercentage={jest.fn()}
            updateFacilityAffiliations={jest.fn()}
            updateFacilityCertifications={jest.fn()}
            updateFacilityProductTypes={jest.fn()}
            updateFacilityProductionTypes={jest.fn()}
            updateContactPerson={jest.fn()}
            updateContactEmail={jest.fn()}
            updateOfficeName={jest.fn()}
            updateOfficeAddress={jest.fn()}
            updateOfficeCountry={jest.fn()}
            updateOfficePhone={jest.fn()}
            submitUpdate={jest.fn()}
            updating={false}
            updateFacilityPhoneVisibility={jest.fn()}
            updateContactVisibility={jest.fn()}
            updateOfficeVisibility={jest.fn()}
            errorUpdating={null}
            updateParentCompany={jest.fn()}
            sectorOptions={[]}
            fetchSectors={jest.fn()}
            updateOpeningDate={jest.fn()}
            updateClosingDate={jest.fn()}
            updateEstimatedAnnualThroughput={jest.fn()}
            energyValueUpdaters={{
                energyCoal: jest.fn(),
                energyNaturalGas: jest.fn(),
                energyDiesel: jest.fn(),
                energyKerosene: jest.fn(),
                energyBiomass: jest.fn(),
                energyCharcoal: jest.fn(),
                energyAnimalWaste: jest.fn(),
                energyElectricity: jest.fn(),
                energyOther: jest.fn(),
            }}
            energyEnabledUpdaters={{
                energyCoal: jest.fn(),
                energyNaturalGas: jest.fn(),
                energyDiesel: jest.fn(),
                energyKerosene: jest.fn(),
                energyBiomass: jest.fn(),
                energyCharcoal: jest.fn(),
                energyAnimalWaste: jest.fn(),
                energyElectricity: jest.fn(),
                energyOther: jest.fn(),
            }}
            userHasSignedIn
            classes={{}}
        />,
        { preloadedState },
    );

describe('ClaimedFacilitiesDetails', () => {
    it('renders primary section headings', () => {
        renderComponent();

        expect(screen.getByText('Facility Details')).toBeInTheDocument();
        expect(screen.getByText('Free Emissions Estimates')).toBeInTheDocument();
        expect(
            screen.getByText('Actual Annual Energy Consumption'),
        ).toBeInTheDocument();
    });

    it('renders opening and closing date inputs', () => {
        renderComponent();

        expect(screen.getByText('Opening Date')).toBeInTheDocument();
        expect(screen.getByText('Closing Date')).toBeInTheDocument();
    });
});

