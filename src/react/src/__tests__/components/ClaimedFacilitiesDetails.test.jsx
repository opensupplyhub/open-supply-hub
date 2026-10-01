import React from 'react';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimedFacilitiesDetails from '../../components/ClaimedFacilitiesDetails/ClaimedFacilitiesDetails';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
}));

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

const renderComponent = (overrides = {}) =>
    renderWithProviders(
        <MemoryRouter>
        <ClaimedFacilitiesDetails
            match={{ params: { claimID: '123' } }}
            user={preloadedState.auth.user.user}
            fetching={false}
            errors={null}
            data={baseClaimData}
            getDetails={jest.fn()}
            clearDetails={jest.fn()}
            updateFacilityNameNativeLanguage={jest.fn()}
            updateFacilityNameEnglish={jest.fn()}
            updateFacilityAddress={jest.fn()}
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
            {...overrides}
        />
        </MemoryRouter>,
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

    it('renders opening date input', () => {
        renderComponent();

        expect(screen.getByText('Opening Date')).toBeInTheDocument();
    });

    it('hides the English name and address fields while the switch is off', () => {
        renderComponent({ isNameAddressEditable: false });

        expect(
            screen.queryByTestId('input-Facility name (English)'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByTestId('input-Facility address'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByText(/should match the name and address/),
        ).not.toBeInTheDocument();
        expect(
            screen.getByTestId('input-Facility name (native language)'),
        ).toBeInTheDocument();
    });

    it('renders the English name and address fields with a note while the switch is on', () => {
        renderComponent({ isNameAddressEditable: true });

        expect(
            screen.getByTestId('input-Facility name (English)'),
        ).toBeInTheDocument();
        expect(
            screen.getByTestId('input-Facility address'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(/should match the name and address/),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('link', {
                name: /Single Location Contribution form/,
            }),
        ).toHaveAttribute('href', '/contribute/single-location');
    });

    it('requires the English name and address while the switch is on', () => {
        renderComponent({
            isNameAddressEditable: true,
            data: {
                ...baseClaimData,
                facility_name_english: '',
                facility_address: '   ',
            },
        });

        expect(
            screen.getByText('Facility name is required'),
        ).toBeInTheDocument();
        expect(
            screen.getByText('Facility address is required'),
        ).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
    });

    it('does not let a hidden English name block saving while the switch is off', () => {
        renderComponent({
            isNameAddressEditable: false,
            data: { ...baseClaimData, facility_name_english: 'a'.repeat(201) },
        });

        expect(
            screen.queryByText('Facility name must be 200 characters or fewer'),
        ).not.toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Save' })).toBeEnabled();
    });

    it('shows a validation error for an over-long English name', () => {
        renderComponent({
            isNameAddressEditable: true,
            data: { ...baseClaimData, facility_name_english: 'a'.repeat(201) },
        });

        expect(
            screen.getByText('Facility name must be 200 characters or fewer'),
        ).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
    });

    describe('quality check on save', () => {
        const warning = {
            type: 'name_quality',
            title: 'Name May Not Look Like a Facility Name',
            message: 'Looks like test data.',
        };
        const loadedNameAddress = {
            name: 'Loaded Name',
            address: '123 Test St',
        };
        const checkURL = '/api/facilities/fac-1/claim/quality-check/';

        beforeEach(() => {
            apiRequest.post.mockReset();
        });

        it('checks a changed name before saving and shows the warnings', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(screen.getByText(warning.title)).toBeInTheDocument();
            });
            expect(apiRequest.post).toHaveBeenCalledWith(checkURL, {
                facility_name_english: 'Mock Facility',
                facility_address: '123 Test St',
            });
            expect(submitUpdate).not.toHaveBeenCalled();
        });

        it('"Save anyway" saves with the dismissed warnings', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));
            await waitFor(() => {
                expect(screen.getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(screen.getByText('Save anyway'));

            expect(submitUpdate).toHaveBeenCalledWith([
                { type: 'name_quality', message: 'Looks like test data.' },
            ]);
        });

        it('"Go back and edit" closes the dialog without saving', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));
            await waitFor(() => {
                expect(screen.getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(screen.getByText('Go back and edit'));

            await waitFor(() => {
                expect(
                    screen.queryByText(warning.title),
                ).not.toBeInTheDocument();
            });
            expect(submitUpdate).not.toHaveBeenCalled();
        });

        it('re-shows the warnings on a second Save with the same values without a second request', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));
            await waitFor(() => {
                expect(screen.getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(screen.getByText('Go back and edit'));
            // The dialog leaves the DOM after its close transition; the
            // page behind it is aria-hidden until then.
            await waitFor(() => {
                expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(screen.getByText(warning.title)).toBeInTheDocument();
            });
            expect(apiRequest.post).toHaveBeenCalledTimes(1);
            expect(submitUpdate).not.toHaveBeenCalled();
        });

        it('saves directly when the name and address are unchanged', async () => {
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress: {
                    name: 'mock facility ',
                    address: '123 Test St',
                },
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(submitUpdate).toHaveBeenCalledWith([]);
            });
            expect(apiRequest.post).not.toHaveBeenCalled();
        });

        it('saves when the check returns no warnings', async () => {
            apiRequest.post.mockResolvedValue({ data: { warnings: [] } });
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(submitUpdate).toHaveBeenCalledWith([]);
            });
        });

        it('saves when the check request fails (fail open)', async () => {
            apiRequest.post.mockRejectedValue(new Error('network'));
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: true,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(submitUpdate).toHaveBeenCalledWith([]);
            });
        });

        it('does not check while the switch is off', async () => {
            const submitUpdate = jest.fn();
            renderComponent({
                isNameAddressEditable: false,
                loadedNameAddress,
                submitUpdate,
            });

            fireEvent.click(screen.getByRole('button', { name: 'Save' }));

            await waitFor(() => {
                expect(submitUpdate).toHaveBeenCalledWith([]);
            });
            expect(apiRequest.post).not.toHaveBeenCalled();
        });
    });
});
