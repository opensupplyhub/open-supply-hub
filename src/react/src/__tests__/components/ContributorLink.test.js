import React from 'react';
import { render, screen } from '@testing-library/react';
import moment from 'moment';
import ContributorLink from '../../components/ProductionLocation/PartnerSection/PartnerSectionItem/ContributorLink';

const defaultProps = {
    created_at: '2024-06-15T10:30:00Z',
    contributor_id: 42,
    contributor_name: 'Acme Corp',
};

describe('ContributorLink', () => {
    it('renders a formatted date', () => {
        render(<ContributorLink {...defaultProps} />);

        const expected = moment('2024-06-15T10:30:00Z').format('LL');
        expect(screen.getByText(new RegExp(expected))).toBeInTheDocument();
    });

    it('renders a link to the contributor profile', () => {
        render(<ContributorLink {...defaultProps} />);

        const link = screen.getByRole('link', { name: 'Acme Corp' });
        expect(link).toHaveAttribute('href', '/profile/42');
    });

    it('opens the link in a new tab with secure rel', () => {
        render(<ContributorLink {...defaultProps} />);

        const link = screen.getByRole('link');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
});
