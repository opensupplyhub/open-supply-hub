/* eslint-env jest */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import EvidencePanel, { buildUrlEvidence } from '../../components/ClaimsV2/EvidencePanel';

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

    it('resolves a legacy .json source name to its attachment', () => {
        // Legacy blocks name the extract source by the derived artifact
        // ("registration-document.json"); the request must still open
        // registration-document.pdf, like the text lookup does.
        const { rerender } = render(
            <EvidencePanel attachments={ATTACHMENTS} claimID={1} />,
        );
        rerender(
            <EvidencePanel
                attachments={ATTACHMENTS}
                claimID={1}
                requestedDoc={{ name: 'registration-document.json', seq: 1 }}
            />,
        );
        expect(window.open).toHaveBeenCalledWith(
            'http://x/3',
            '_blank',
            'noopener',
        );
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

    it('handles a doc with neither URL nor id without broken links', () => {
        render(
            <EvidencePanel
                attachments={[{ file_name: 'orphan.pdf' }]}
                claimID={7}
            />,
        );
        fireEvent.click(screen.getByRole('button', { name: /orphan\.pdf/ }));
        expect(window.open).not.toHaveBeenCalled();
        expect(
            screen.getByText(/original unavailable until the download/),
        ).toBeInTheDocument();
    });
});

describe('buildUrlEvidence', () => {
    it('collects, labels, normalizes and dedupes the four URL fields', () => {
        const detail = {
            facility_website: 'https://example-winery.com/fr',
            website: 'example-winery.com/fr', // scheme-less dupe of the above
            linkedin_profile: '',
            claimant_linkedin_profile_url: 'https://www.linkedin.com/in/example',
        };
        expect(buildUrlEvidence(detail)).toEqual([
            {
                file_name: 'https://example-winery.com/fr',
                label: 'Production location website',
                is_url: true,
            },
            {
                file_name: 'https://www.linkedin.com/in/example',
                label: 'Claimant LinkedIn',
                is_url: true,
            },
        ]);
    });

    it('drops free-text values that are not URLs', () => {
        // The legacy `website` field is free text; none of these may
        // become a clickable chip or count as evidence.
        ['N/A', 'none', 'www.a.com, www.b.com'].forEach(website => {
            expect(buildUrlEvidence({ website })).toEqual([]);
        });
    });

    it('normalizes schemes case-insensitively and completely', () => {
        // A bare host that merely starts with "http" still needs the
        // prefix — startsWith('http') used to skip it, and the evidence
        // was then dropped at protocol validation.
        expect(buildUrlEvidence({ website: 'httpbin.org' })).toEqual([
            {
                file_name: 'https://httpbin.org',
                label: 'Business website',
                is_url: true,
            },
        ]);
        // Schemes are case-insensitive: an uppercase scheme is already
        // complete and must not be double-prefixed.
        expect(buildUrlEvidence({ website: 'HTTP://X.COM' })).toEqual([
            { file_name: 'HTTP://X.COM', label: 'Business website', is_url: true },
        ]);
    });

    it('returns nothing for blank or absent fields', () => {
        expect(buildUrlEvidence({})).toEqual([]);
        expect(buildUrlEvidence({ website: '   ' })).toEqual([]);
        expect(buildUrlEvidence(undefined)).toEqual([]);
    });
});

describe('EvidencePanel URL evidence', () => {
    beforeEach(() => {
        window.open = jest.fn();
    });

    const URL_DOC = {
        file_name: 'https://example-winery.com/fr',
        label: 'Production location website',
        is_url: true,
    };
    const REVIEW = {
        evidence: {
            'https://example-winery.com/fr': {
                kind: 'url',
                translated: 'Example Winery, Exampletown',
            },
        },
    };

    it('renders a link chip after the attachments and counts it', () => {
        render(
            <EvidencePanel
                attachments={ATTACHMENTS}
                urlEvidence={[URL_DOC]}
                claimID={1}
            />,
        );
        expect(screen.getByText(/Evidence \(4\)/)).toBeInTheDocument();
        expect(
            screen.getByText(/🔗 Production location website/),
        ).toBeInTheDocument();
    });

    it('opens the link in a new tab and shows the page text inline', () => {
        render(
            <EvidencePanel
                attachments={ATTACHMENTS}
                urlEvidence={[URL_DOC]}
                review={REVIEW}
                claimID={1}
            />,
        );
        fireEvent.click(screen.getByText(/🔗 Production location website/));
        expect(window.open).toHaveBeenCalledWith(
            'https://example-winery.com/fr',
            '_blank',
            'noopener',
        );
        expect(
            screen.getByText(/Example Winery, Exampletown/),
        ).toBeInTheDocument();
    });

    it('degrades to an open-the-link hint when the block has no page text', () => {
        render(
            <EvidencePanel
                attachments={[]}
                urlEvidence={[URL_DOC]}
                claimID={1}
            />,
        );
        // Auto-opened (only doc) without spawning a tab.
        expect(window.open).not.toHaveBeenCalled();
        expect(
            screen.getByText(/No page text recorded for this link/),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('link', { name: /open the link/ }),
        ).toHaveAttribute('href', 'https://example-winery.com/fr');
    });
});
