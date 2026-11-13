import React from 'react';
import { render, screen } from '@testing-library/react';
import BetaChip, { BETA_CHIP_TEXT } from '../../components/Shared/BetaChip/BetaChip';

describe('BetaChip component', () => {
    test('renders the Beta text', () => {
        render(<BetaChip />);

        expect(screen.getByTestId('beta-chip')).toHaveTextContent(
            BETA_CHIP_TEXT,
        );
    });

    test('appends a custom class name', () => {
        render(<BetaChip className="custom" />);

        expect(screen.getByTestId('beta-chip')).toHaveClass('custom');
    });
});
