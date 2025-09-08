import React from 'react';

import DownloadLimitInfo from '../../components/DownloadLimitInfo';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('DownloadLimitInfo component', () => {
    const renderComponent = () =>
        renderWithProviders(<DownloadLimitInfo />);

    test('renders all main text content and paragraphs', () => {
        const { getByText, container } = renderComponent();

        // Check all three main text messages.
        expect(
            getByText(
                /All registered accounts can download up to 5000 production locations annually for free\./
            )
        ).toBeInTheDocument();
        expect(
            getByText(
                /This search includes more production locations than you have available for download\. You may purchase additional downloads to continue\./
            )
        ).toBeInTheDocument();
        expect(
            getByText(
                /If you are from a civil society organization or research institution, you may qualify for discounted or unlimited free download access\./
            )
        ).toBeInTheDocument();

        // Check that all three paragraphs are present.
        const paragraphs = container.querySelectorAll('p');
        expect(paragraphs).toHaveLength(3);
    });

    test('renders the "Learn more and apply" link with correct attributes', () => {
        const { getByText } = renderComponent();

        const link = getByText('Learn more and apply');
        expect(link).toBeInTheDocument();
        expect(link.tagName).toBe('A');
        expect(link).toHaveAttribute(
            'href',
            'https://info.opensupplyhub.org/governance-policies'
        );
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    test('renders the component with proper structure', () => {
        const { container } = renderComponent();

        // Check that the component renders without errors.
        expect(container.firstChild).toBeInTheDocument();

        // Check that Grid components are present.
        const gridContainers = container.querySelectorAll(
            '[class*="informativeWrapper"]'
        );
        expect(gridContainers.length).toBeGreaterThan(0);
    });
}); 