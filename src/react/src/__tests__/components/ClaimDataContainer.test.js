import React from 'react';
import { fireEvent, waitFor } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimDataContainer from '../../components/ProductionLocation/ClaimSection/ClaimDataContainer/ClaimDataContainer';
import { STATUS_CLAIMED } from '../../components/ProductionLocation/DataPoint/constants';

const makeClaimInfo = (overrides = {}) => ({
    facility: {
        website: 'https://example.com',
        phone_number: '+1 234 567 8900',
        minimum_order: '100 units',
        average_lead_time: '30 days',
        female_workers_percentage: 60,
        affiliations: ['Fair Trade'],
        certifications: ['ISO 9001'],
        opening_date: '2010',
        closing_date: null,
        estimated_annual_throughput: 20000,
        actual_annual_energy_consumption: null,
        description: 'A sample facility.',
    },
    contact: {
        name: 'Jane Doe',
        email: 'jane@example.com',
    },
    office: {
        name: 'Head Office',
        address: '1 Office St',
        country: 'US',
        phone_number: '+1 800 000 0000',
    },
    contributor: { name: 'Test Contributor' },
    approved_at: '2023-05-15T00:00:00Z',
    created_at: '2023-01-01T00:00:00Z',
    ...overrides,
});

const renderComponent = (props = {}) => {
    const claimInfo =
        'claimInfo' in props ? props.claimInfo : makeClaimInfo();
    return renderWithProviders(
        <ClaimDataContainer
            isClaimed={props.isClaimed ?? true}
            claimInfo={claimInfo}
            className={props.className}
        />,
    );
};

describe('ClaimDataContainer — empty state', () => {
    it('renders nothing when isClaimed is false', () => {
        const { container } = renderComponent({ isClaimed: false });
        expect(container.firstChild).toBeNull();
    });

    it('renders nothing when claimInfo is null', () => {
        const { container } = renderComponent({
            isClaimed: true,
            claimInfo: null,
        });
        expect(container.firstChild).toBeNull();
    });

    it('renders nothing when all facility fields are empty', () => {
        const { container } = renderComponent({
            claimInfo: makeClaimInfo({
                facility: {},
                contact: null,
                office: null,
            }),
        });
        expect(container.firstChild).toBeNull();
    });
});

describe('ClaimDataContainer — section header', () => {
    it('renders the section title', () => {
        const { getByText } = renderComponent();
        expect(
            getByText('Operational Details Submitted by Management'),
        ).toBeInTheDocument();
    });

    it('renders the info tooltip trigger', () => {
        const { getByTestId } = renderComponent();
        expect(getByTestId('claim-data-info-tooltip')).toBeInTheDocument();
    });

    it('renders the toggle switch', () => {
        const { getByRole } = renderComponent();
        expect(
            getByRole('checkbox', {
                name: /show operational details submitted by management/i,
            }),
        ).toBeInTheDocument();
    });

    it('shows "Open" label when content is open by default', () => {
        const { getByText } = renderComponent();
        expect(getByText('Open')).toBeInTheDocument();
    });

    it('sets the operational-details id on the root element', () => {
        const { container } = renderComponent();
        expect(container.querySelector('#operational-details')).toBeInTheDocument();
    });
});

describe('ClaimDataContainer — field labels and values', () => {
    it('renders all expected field labels', () => {
        const { getByText } = renderComponent();

        const expectedLabels = [
            'Website',
            'Contact Person',
            'Contact Email',
            'Phone Number',
            'Minimum Order',
            'Average Lead Time',
            'Affiliations',
            'Certifications/Standards/Regulations',
            'Opening Date',
            'Estimated Annual Throughput',
            'Office Name',
            'Office Address',
            'Office Phone Number',
            'Description',
        ];

        expectedLabels.forEach(label => {
            expect(getByText(label, { exact: true })).toBeInTheDocument();
        });
    });

    it('renders plain field values', () => {
        const claimInfo = makeClaimInfo();
        const { getByText } = renderComponent({ claimInfo });

        expect(
            getByText(claimInfo.facility.phone_number, { exact: true }),
        ).toBeInTheDocument();
        expect(
            getByText(claimInfo.facility.minimum_order, { exact: true }),
        ).toBeInTheDocument();
        expect(
            getByText(claimInfo.facility.average_lead_time, { exact: true }),
        ).toBeInTheDocument();
        expect(
            getByText(claimInfo.facility.description, { exact: true }),
        ).toBeInTheDocument();
        expect(
            getByText('20000 kg/year', { exact: true }),
        ).toBeInTheDocument();
    });

    it('renders contact fields when contact is provided', () => {
        const { getByText } = renderComponent();
        expect(getByText('Jane Doe', { exact: true })).toBeInTheDocument();
        expect(
            getByText('jane@example.com', { exact: true }),
        ).toBeInTheDocument();
    });

    it('omits contact fields when contact is null', () => {
        const { queryByText } = renderComponent({
            claimInfo: makeClaimInfo({ contact: null }),
        });
        expect(queryByText('Contact Person')).not.toBeInTheDocument();
        expect(queryByText('Contact Email')).not.toBeInTheDocument();
    });

    it('renders office fields when office is provided', () => {
        const { getByText } = renderComponent();
        expect(getByText('Head Office', { exact: true })).toBeInTheDocument();
    });

    it('omits office fields when office is null', () => {
        const { queryByText } = renderComponent({
            claimInfo: makeClaimInfo({ office: null }),
        });
        expect(queryByText('Office Name')).not.toBeInTheDocument();
        expect(queryByText('Office Address')).not.toBeInTheDocument();
        expect(queryByText('Office Phone Number')).not.toBeInTheDocument();
    });

    it('renders female_workers_percentage field when value is 0', () => {
        const { getByText } = renderComponent({
            claimInfo: makeClaimInfo({
                facility: { female_workers_percentage: 0 },
                contact: null,
                office: null,
            }),
        });
        expect(
            getByText('Percentage of female workers', { exact: true }),
        ).toBeInTheDocument();
    });
});

describe('ClaimDataContainer — field ordering', () => {
    it('renders fields in the order defined by FIELD_ORDER', () => {
        const { getAllByTestId } = renderComponent();
        const labels = getAllByTestId('data-point-label').map(
            el => el.textContent,
        );

        const websiteIndex = labels.indexOf('Website');
        const phoneIndex = labels.indexOf('Phone Number');
        const officeNameIndex = labels.indexOf('Office Name');
        const descriptionIndex = labels.indexOf('Description');
        const certificationsIndex = labels.indexOf(
            'Certifications/Standards/Regulations',
        );
        const affiliationsIndex = labels.indexOf('Affiliations');
        const minimumOrderIndex = labels.indexOf('Minimum Order');

        expect(websiteIndex).toBeLessThan(phoneIndex);
        expect(phoneIndex).toBeLessThan(officeNameIndex);
        expect(descriptionIndex).toBeLessThan(certificationsIndex);
        expect(certificationsIndex).toBeLessThan(affiliationsIndex);
        expect(affiliationsIndex).toBeLessThan(minimumOrderIndex);
    });
});

describe('ClaimDataContainer — Claimed status chips', () => {
    it('renders a Claimed chip for each displayed field', () => {
        const { getAllByTestId, getAllByText } = renderComponent();
        const dataPoints = getAllByTestId('data-point');
        const claimedChips = getAllByText(STATUS_CLAIMED);
        expect(claimedChips.length).toBe(dataPoints.length);
    });
});

describe('ClaimDataContainer — contributor attribution', () => {
    it('resolves contributor name from contributor.name object', () => {
        const { getAllByTestId } = renderComponent({
            claimInfo: makeClaimInfo({
                contributor: { name: 'Acme Corp' },
            }),
        });
        getAllByTestId('data-point-contributor').forEach(el => {
            expect(el).toHaveTextContent('Acme Corp');
        });
    });

    it('resolves contributor name from a plain string', () => {
        const { getAllByTestId } = renderComponent({
            claimInfo: makeClaimInfo({ contributor: 'String Contributor' }),
        });
        getAllByTestId('data-point-contributor').forEach(el => {
            expect(el).toHaveTextContent('String Contributor');
        });
    });

    it('prefers approved_at over created_at for the date', () => {
        const { getAllByTestId } = renderComponent({
            claimInfo: makeClaimInfo({
                approved_at: '2023-05-15T00:00:00Z',
                created_at: '2023-01-01T00:00:00Z',
            }),
        });
        getAllByTestId('data-point-date').forEach(el => {
            expect(el).toHaveTextContent('May 15, 2023');
        });
    });

    it('falls back to created_at when approved_at is absent', () => {
        const { getAllByTestId } = renderComponent({
            claimInfo: makeClaimInfo({
                approved_at: undefined,
                created_at: '2022-11-09T00:00:00Z',
            }),
        });
        getAllByTestId('data-point-date').forEach(el => {
            expect(el).toHaveTextContent('November 9, 2022');
        });
    });
});
