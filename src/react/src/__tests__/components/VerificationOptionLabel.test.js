import React from 'react';
import { render, screen } from '@testing-library/react';
import VerificationOptionLabel from '../../components/InitialClaimFlow/Shared/VerificationOptionLabel/VerificationOptionLabel';
import formatVerificationOptionLabel from '../../components/InitialClaimFlow/Shared/VerificationOptionLabel/formatVerificationOptionLabel';

describe('VerificationOptionLabel', () => {
    test('shows the preferred tag beside the label', () => {
        render(
            <VerificationOptionLabel
                label="Business registration document"
                tag="preferred"
            />,
        );

        expect(
            screen.getByText('Business registration document'),
        ).toBeInTheDocument();
        expect(screen.getByText('Preferred')).toBeInTheDocument();
    });

    test('shows the can delay review tag beside the label', () => {
        render(
            <VerificationOptionLabel
                label="Your LinkedIn page showing your name, title and company"
                tag="can-delay"
            />,
        );

        expect(screen.getByText('Can delay review')).toBeInTheDocument();
        expect(screen.queryByText('Preferred')).not.toBeInTheDocument();
    });

    test('shows the label alone when the option has no tag', () => {
        render(<VerificationOptionLabel label="Utility bill" />);

        expect(screen.getByText('Utility bill')).toBeInTheDocument();
        expect(screen.queryByText('Preferred')).not.toBeInTheDocument();
        expect(screen.queryByText('Can delay review')).not.toBeInTheDocument();
    });
});

describe('formatVerificationOptionLabel', () => {
    const option = {
        value: 'linkedin-page',
        label: 'Your LinkedIn page showing your name, title and company',
        tag: 'can-delay',
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
