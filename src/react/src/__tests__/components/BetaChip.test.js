import React from 'react';
import { render, screen } from '@testing-library/react';
import BetaChip, { BETA_CHIP_TEXT } from '../../components/Shared/BetaChip/BetaChip';

describe('BetaChip component', () => {
    test('renders the Beta text', () => {
        render(<BetaChip />);

        expect(screen.getByText(BETA_CHIP_TEXT)).toBeInTheDocument();
    });

    test('appends a custom class name', () => {
        render(<BetaChip className="custom" />);

        expect(screen.getByText(BETA_CHIP_TEXT)).toHaveClass('custom');
    });
});
