import React from 'react';
import { render, screen } from '@testing-library/react';

import ClaimantDetailsPanel from '../../components/ClaimsV2/ClaimantDetailsPanel';

describe('ClaimantDetailsPanel profile visibility (OSDEV-2680)', () => {
    it('shows whether the website and phone are on the profile', () => {
        render(
            <ClaimantDetailsPanel
                detail={{
                    facility_website: 'https://facility.com',
                    facility_website_publicly_visible: true,
                    facility_phone_number: '+1-555-1234',
                    facility_phone_number_publicly_visible: false,
                }}
            />,
        );

        expect(screen.getByText('Production location website')).toBeInTheDocument();
        expect(screen.getByText('Shown on profile')).toBeInTheDocument();
        expect(screen.getByText('Production location phone')).toBeInTheDocument();
        expect(screen.getByText('+1-555-1234')).toBeInTheDocument();
        expect(screen.getByText('Not shown on profile')).toBeInTheDocument();
    });

    it('keeps the website a link when the visibility note is shown', () => {
        render(
            <ClaimantDetailsPanel
                detail={{
                    facility_website: 'https://facility.com',
                    facility_website_publicly_visible: false,
                }}
            />,
        );

        expect(
            screen.getByRole('link', { name: /https:\/\/facility\.com/ }),
        ).toHaveAttribute('href', 'https://facility.com');
        expect(screen.getByText('Not shown on profile')).toBeInTheDocument();
    });

    it('omits the rows when the claimant gave no website or phone', () => {
        render(
            <ClaimantDetailsPanel
                detail={{
                    linkedin_profile: 'https://linkedin.com/company/facility',
                    facility_website_publicly_visible: true,
                    facility_phone_number_publicly_visible: true,
                }}
            />,
        );

        expect(
            screen.queryByText('Production location website'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByText('Production location phone'),
        ).not.toBeInTheDocument();
        expect(screen.queryByText('Shown on profile')).not.toBeInTheDocument();
    });
});
