import React from 'react';
import { render, screen } from '@testing-library/react';
import VerificationOptionLabel, {
    formatVerificationOptionLabel,
} from '../../components/InitialClaimFlow/Shared/VerificationOptionLabel/VerificationOptionLabel';

describe('VerificationOptionLabel', () => {
    test.each(['Preferred', 'Can delay review'])(
        'shows the "%s" tag beside the label',
        tag => {
            render(<VerificationOptionLabel label="Utility bill" tag={tag} />);

            expect(screen.getByText('Utility bill')).toBeInTheDocument();
            expect(screen.getByText(tag)).toBeInTheDocument();
        },
    );
});

describe('formatVerificationOptionLabel', () => {
    const option = {
        value: 'linkedin-page',
        label: 'Your LinkedIn page showing your name, title and company',
        tag: 'Can delay review',
    };

    test('shows the tag in the open list', () => {
        render(formatVerificationOptionLabel(option, { context: 'menu' }));

        expect(screen.getByText(option.label)).toBeInTheDocument();
        expect(screen.getByText('Can delay review')).toBeInTheDocument();
    });

    test('shows the label alone for the chosen value', () => {
        expect(formatVerificationOptionLabel(option, { context: 'value' })).toBe(
            option.label,
        );
    });
});
