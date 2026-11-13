import React from 'react';
import { render, screen } from '@testing-library/react';
import WhyBetaCard from '../../components/ProductionLocation/PartnerSection/WhyBetaCard/WhyBetaCard';
import {
    WHY_BETA_TITLE,
    WHY_BETA_BODY,
    WHY_BETA_LINK_TEXT,
    WHY_BETA_LINK_HREF,
} from '../../components/ProductionLocation/PartnerSection/WhyBetaCard/constants';

describe('WhyBetaCard component', () => {
    test('renders the chip, title, body and suggestions link', () => {
        render(<WhyBetaCard />);

        expect(screen.getByTestId('why-beta-card')).toBeInTheDocument();
        expect(screen.getByTestId('beta-chip')).toBeInTheDocument();
        expect(screen.getByText(WHY_BETA_TITLE)).toBeInTheDocument();
        expect(screen.getByText(WHY_BETA_BODY)).toBeInTheDocument();

        const link = screen.getByRole('link', { name: WHY_BETA_LINK_TEXT });
        expect(link).toHaveAttribute('href', WHY_BETA_LINK_HREF);
    });

    test('the suggestions link opens an email to support', () => {
        expect(WHY_BETA_LINK_HREF).toMatch(/^mailto:support@opensupplyhub\.org/);
    });
});
