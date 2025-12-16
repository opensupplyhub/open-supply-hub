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
    facility_name_native_language: 'Name',
    sector: [],
    facility_phone_number: '',
    facility_phone_number_publicly_visible: false,
    facility_website: '',
    facility_website_publicly_visible: false,
    facility_description: '',
    facility_address: '123 Test St',
    facility_parent_company: { id: null, name: '' },
    parent_company_name: '',
    facility_name_english: '',
    facility_minimum_order_quantity: '',
    facility_average_lead_time: '',
    facility_workers_count: '',
    facility_female_workers_percentage: '',
    facility_affiliations: [],
    facility_certifications: [],
    facility_production_types: [],
    facility_product_types: [],
    point_of_contact_publicly_visible: false,
    point_of_contact_person_name: '',
    point_of_contact_email: '',
    office_info_publicly_visible: false,
    office_official_name: '',
    office_address: '',
    office_country_code: '',
    office_phone_number: '',
    countries: [],
    affiliation_choices: [],
    certification_choices: [],
    production_type_choices: [],
    opening_date: '',
    closing_date: '',
    estimated_annual_throughput: '',
    energy_coal: '',
    energy_natural_gas: '',
    energy_diesel: '',
    energy_kerosene: '',
    energy_biomass: '',
    energy_charcoal: '',
    energy_animal_waste: '',
    energy_electricity: '',
    energy_other: '',
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
            updateEnergyCoal={jest.fn()}
            updateEnergyNaturalGas={jest.fn()}
            updateEnergyDiesel={jest.fn()}
            updateEnergyKerosene={jest.fn()}
            updateEnergyBiomass={jest.fn()}
            updateEnergyCharcoal={jest.fn()}
            updateEnergyAnimalWaste={jest.fn()}
            updateEnergyElectricity={jest.fn()}
            updateEnergyOther={jest.fn()}
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

