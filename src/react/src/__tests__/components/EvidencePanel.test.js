/* eslint-env jest */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import EvidencePanel from '../../components/ClaimsV2/EvidencePanel';

const ATTACHMENTS = [
    { id: 11, file_name: 'utility-bill.png', claim_attachment: 'http://x/1' },
    {
        id: 12,
        file_name: 'employment-letter.png',
        claim_attachment: 'http://x/2',
    },
    {
        id: 13,
        file_name: 'registration-document.pdf',
        claim_attachment: 'http://x/3',
    },
];

const viewerName = () =>
    document.querySelector('[aria-label="Evidence"] span').textContent;

describe('EvidencePanel', () => {
    beforeEach(() => {
        window.open = jest.fn();
    });

    it('auto-opens the first document', () => {
        render(<EvidencePanel attachments={ATTACHMENTS} claimID={1} />);
        expect(
            screen.getByAltText('utility-bill.png'),
        ).toBeInTheDocument();
    });

    it('switches the viewer when another chip is clicked', () => {
        render(<EvidencePanel attachments={ATTACHMENTS} claimID={1} />);
        fireEvent.click(screen.getByText(/employment-letter\.png/));
        expect(
            screen.getByAltText('employment-letter.png'),
        ).toBeInTheDocument();
        expect(window.open).not.toHaveBeenCalled();
    });

    it('opens a PDF in a new tab and shows the hint inline', () => {
        render(<EvidencePanel attachments={ATTACHMENTS} claimID={1} />);
        fireEvent.click(screen.getByText(/registration-document\.pdf/));
        expect(window.open).toHaveBeenCalledWith(
            'http://x/3',
            '_blank',
            'noopener',
        );
    });

    it('opens a requested document from the verification rows', () => {
        const { rerender } = render(
            <EvidencePanel attachments={ATTACHMENTS} claimID={1} />,
        );
        rerender(
            <EvidencePanel
                attachments={ATTACHMENTS}
                claimID={1}
                requestedDoc={{ name: 'employment-letter.png', seq: 1 }}
            />,
        );
        expect(
            screen.getByAltText('employment-letter.png'),
        ).toBeInTheDocument();
    });

    it('falls back to the download endpoint without claim_attachment', () => {
        render(
            <EvidencePanel
                attachments={[{ id: 9, file_name: 'doc.png' }]}
                claimID={7}
            />,
        );
        expect(screen.getByAltText('doc.png')).toHaveAttribute(
            'src',
            '/api/facility-claims/7/attachments/9/download/',
        );
    });
});
