import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import AnnouncementBanner from '../../components/Navbar/AnnouncementBanner';

const CONTENT_HTML =
    '<p>Support Open Supply Hub! <a href="https://example.test/donate">Give today</a></p>';

const renderBanner = banner =>
    renderWithProviders(<AnnouncementBanner />, {
        preloadedState: {
            announcementBanner: {
                fetching: false,
                banner,
            },
            embeddedMap: { embed: false },
        },
    });

describe('AnnouncementBanner', () => {
    test('renders nothing when the banner is inactive', () => {
        const { container } = renderBanner({
            is_active: false,
            content: CONTENT_HTML,
        });

        expect(container).toBeEmptyDOMElement();
    });

    test('renders nothing when the banner is active but has no content', () => {
        const { container } = renderBanner({ is_active: true, content: '' });

        expect(container).toBeEmptyDOMElement();
    });

    test('renders the admin-authored content when active', () => {
        renderBanner({ is_active: true, content: CONTENT_HTML });

        expect(
            screen.getByText(/Support Open Supply Hub!/),
        ).toBeInTheDocument();
    });

    test('renders links from the content', () => {
        renderBanner({ is_active: true, content: CONTENT_HTML });

        const link = screen.getByRole('link', { name: 'Give today' });
        expect(link).toHaveAttribute('href', 'https://example.test/donate');
    });
});
