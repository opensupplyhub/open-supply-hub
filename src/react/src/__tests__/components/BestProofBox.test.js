import React from 'react';
import { render } from '@testing-library/react';
import BestProofBox from '../../components/InitialClaimFlow/Shared/BestProofBox/BestProofBox';
import {
    EMAIL_BEST_PROOF,
    COMPANY_ADDRESS_BEST_PROOF,
    EMPLOYMENT_BEST_PROOF,
} from '../../components/InitialClaimFlow/Shared/BestProofBox/constants';

const linesOf = container =>
    Array.from(container.querySelectorAll('p')).map(line => line.textContent);

describe('BestProofBox component', () => {
    test('renders the title, then the details, then the delays', () => {
        const { container } = render(
            <BestProofBox
                title="Best: this."
                details={['One. Two.']}
                delays={['That can delay approval.']}
            />,
        );

        expect(linesOf(container)).toEqual([
            'Best: this.',
            'One. Two.',
            'That can delay approval.',
        ]);
    });

    test('renders with a title only', () => {
        const { container } = render(<BestProofBox title="Best: this." />);

        expect(linesOf(container)).toEqual(['Best: this.']);
    });

    test('shows the email wording', () => {
        const { container } = render(<BestProofBox {...EMAIL_BEST_PROOF} />);

        expect(linesOf(container)).toEqual([
            'Use your work email.',
            'Example: name@yourcompany.com',
            'A personal email may not be accepted and can significantly delay approval.',
            'No work email? Upload a document with your name and your company.',
        ]);
    });

    test('shows the company address proof wording', () => {
        const { container } = render(
            <BestProofBox {...COMPANY_ADDRESS_BEST_PROOF} />,
        );

        expect(linesOf(container)).toEqual([
            'Best: an official document.',
            'Utility bill. Business registration. Tax document. Business license.',
            'A company website link can delay approval.',
            'A LinkedIn page may not be accepted and can significantly delay approval.',
        ]);
    });

    test('shows the employment proof wording', () => {
        const { container } = render(
            <BestProofBox {...EMPLOYMENT_BEST_PROOF} />,
        );

        expect(linesOf(container)).toEqual([
            'Best: a document with your name and your company.',
            'Business card. Employment letter. ID badge.',
            'A LinkedIn link may not be accepted and can significantly delay approval.',
        ]);
    });
});
