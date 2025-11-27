import React from 'react';

import FacilityDetailsClaimedInfo from '../../components/FacilityDetailsClaimedInfo/FacilityDetailsClaimedInfo';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('FacilityDetailsClaimedInfo component', () => {
    const renderComponent = (data) => renderWithProviders(
        <FacilityDetailsClaimedInfo data={data} />
    );

    test('should display all facility, contact, and office information', () => {
        const data = {
            id: 123,
            facility: {
                description: 'Some description',
                name_english: 'Facility name',
                address: 'Address field',
                website: 'www.test.com',
                country: 'Canada',
                phone_number: '+123 456 7890',
                minimum_order: '18',
                average_lead_time: '120 days',
                opening_date: '2020-01-15',
                closing_date: '2025-12-31',
                estimated_annual_throughput: 50000,
                actual_annual_energy_consumption: {
                    electricity: 1200,
                    natural_gas: 5000000,
                    coal: 3000000,
                    diesel: 1500000,
                },
                parent_company: {
                    id: 10,
                    name: 'Parent company name',
                },
            },
            contact: {
                name: 'John',
                email: 'Doe',
            },
            office: {
                name: 'Sample office name',
                address: 'Sample office address',
                country: 'Canada',
                phone_number: '+098 765 4321',
            },
        };

        const { getByText } = renderComponent(data);

        // Test field labels.
        expect(getByText('Website', { exact: true })).toBeInTheDocument();
        expect(getByText('Contact Person', { exact: true })).toBeInTheDocument();
        expect(getByText('Contact Email', { exact: true })).toBeInTheDocument();
        expect(getByText('Phone Number', { exact: true })).toBeInTheDocument();
        expect(getByText('Minimum Order', { exact: true })).toBeInTheDocument();
        expect(getByText('Average Lead Time', { exact: true })).toBeInTheDocument();
        expect(getByText('Opening Date', { exact: true })).toBeInTheDocument();
        expect(getByText('Closing Date', { exact: true })).toBeInTheDocument();
        expect(getByText('Estimated Annual Throughput', { exact: true })).toBeInTheDocument();
        expect(getByText('Actual Annual Energy Consumption', { exact: true })).toBeInTheDocument();
        expect(getByText('Office Name', { exact: true })).toBeInTheDocument();
        expect(getByText('Office Address', { exact: true })).toBeInTheDocument();
        expect(getByText('Office Phone Number', { exact: true })).toBeInTheDocument();
        expect(getByText('Description', { exact: true })).toBeInTheDocument();

        const plainFieldsToTest = [
            data.facility.website,
            data.facility.country,
            data.facility.phone_number,
            data.facility.minimum_order,
            data.facility.average_lead_time,
            data.contact.name,
            data.contact.email,
            data.office.name,
            data.office.address,
            data.office.country,
            data.office.phone_number,
        ];

        plainFieldsToTest.forEach(fieldText => {
            const textElement = getByText(fieldText, { exact: false });
            expect(textElement).toBeInTheDocument();
        });

        // Test opening and closing dates.
        expect(getByText('January 15, 2020', { exact: true })).toBeInTheDocument();
        expect(getByText('December 31, 2025', { exact: true })).toBeInTheDocument();

        // Test estimated annual throughput.
        expect(getByText('50000 kg/year', { exact: true })).toBeInTheDocument();

        // Test actual annual energy consumption fields.
        expect(getByText('Electricity: 1200 MWh', { exact: true })).toBeInTheDocument();
        expect(getByText('Natural Gas: 5000000 Joules', { exact: true })).toBeInTheDocument();
        expect(getByText('Coal: 3000000 Joules', { exact: true })).toBeInTheDocument();
        expect(getByText('Diesel: 1500000 Joules', { exact: true })).toBeInTheDocument();
    });
});
