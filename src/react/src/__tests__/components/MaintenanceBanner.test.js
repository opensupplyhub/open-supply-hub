import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import MaintenanceBanner from '../../components/Navbar/MaintenanceBanner';

const HEADLINE_TEXT =
    'Open Supply Hub is currently undergoing planned maintenance.';
const BODY_LINE_1 =
    'You can still search and browse, but data uploads are temporarily unavailable.';
const BODY_LINE_2 =
    'Full service will resume shortly. Thank you for your patience.';

const renderBanner = (disableListUploading = false) =>
    renderWithProviders(<MaintenanceBanner />, {
        preloadedState: {
            featureFlags: {
                fetching: false,
                flags: {
                    disable_list_uploading: disableListUploading,
                },
            },
            embeddedMap: { embed: false },
        },
    });

describe('MaintenanceBanner', () => {
    test('renders nothing when disable_list_uploading is inactive', () => {
        const { container } = renderBanner(false);

        expect(container).toBeEmptyDOMElement();
    });

    test('renders the banner when disable_list_uploading is active', () => {
        renderBanner(true);

        expect(screen.getByText(HEADLINE_TEXT)).toBeInTheDocument();
        expect(screen.getByText(BODY_LINE_1)).toBeInTheDocument();
        expect(screen.getByText(BODY_LINE_2)).toBeInTheDocument();
    });

    test('does not render banner text when flag is inactive', () => {
        renderBanner(false);

        expect(screen.queryByText(HEADLINE_TEXT)).not.toBeInTheDocument();
        expect(screen.queryByText(BODY_LINE_1)).not.toBeInTheDocument();
        expect(screen.queryByText(BODY_LINE_2)).not.toBeInTheDocument();
    });

    test('renders headline as bold (strong font weight)', () => {
        renderBanner(true);

        const headline = screen.getByText(HEADLINE_TEXT);
        expect(headline).toBeInTheDocument();
        expect(headline.tagName.toLowerCase()).toBe('p');
    });
});
