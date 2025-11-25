import React from 'react';

import FacilityDetailsClaimedInfo from '../../components/FacilityDetailsClaimedInfo/FacilityDetailsClaimedInfo';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('FacilityDetailsClaimedInfo component', () => {
    test('test facility details presence', () => {
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

      const { getByText } = renderWithProviders(
          <FacilityDetailsClaimedInfo data={ data } />
      );

      const fieldsToTest = [
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

      fieldsToTest.forEach(fieldText => {
        const textElement = getByText(fieldText, { exact: false });
        expect(textElement).toBeInTheDocument();
      });
    })
});
