import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import NavBar from '../../components/ProductionLocation/Sidebar/NavBar/NavBar';

const mockGroups = [
    {
        uuid: 'group-1',
        name: 'Certifications',
        icon_file: 'https://example.com/icons/cert.png',
    },
    {
        uuid: 'group-2',
        name: 'Supply Chain',
        icon_file: 'https://example.com/icons/chain.png',
    },
];

const renderNavBar = (preloadedState = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <NavBar />
        </MemoryRouter>,
        { preloadedState },
    );

describe('NavBar', () => {
    test('renders the "Jump to" heading', () => {
        renderNavBar();

        expect(screen.getByText('Jump to')).toBeInTheDocument();
    });

    test('renders default navigation items when no groups are loaded', () => {
        renderNavBar();

        expect(screen.getByText('Overview')).toBeInTheDocument();
        expect(screen.getByText('General Information')).toBeInTheDocument();
        expect(screen.getByText('Operational Details')).toBeInTheDocument();
    });

    test('renders partner field group items alongside defaults', () => {
        renderNavBar({
            partnerFieldGroups: {
                fetching: false,
                data: { results: mockGroups },
                error: null,
            },
        });

        expect(screen.getByText('Overview')).toBeInTheDocument();
        expect(screen.getByText('General Information')).toBeInTheDocument();
        expect(screen.getByText('Operational Details')).toBeInTheDocument();

        expect(screen.getByText('Certifications')).toBeInTheDocument();
        expect(screen.getByText('Supply Chain')).toBeInTheDocument();
    });

    test('renders group icons with correct src and alt', () => {
        renderNavBar({
            partnerFieldGroups: {
                fetching: false,
                data: { results: mockGroups },
                error: null,
            },
        });

        const certImg = screen.getByAltText('Certifications');
        expect(certImg).toHaveAttribute(
            'src',
            'https://example.com/icons/cert.png',
        );

        const chainImg = screen.getByAltText('Supply Chain');
        expect(chainImg).toHaveAttribute(
            'src',
            'https://example.com/icons/chain.png',
        );
    });

    test('renders only default items when data is null', () => {
        renderNavBar({
            partnerFieldGroups: {
                fetching: false,
                data: null,
                error: null,
            },
        });

        expect(screen.getAllByRole('menuitem')).toHaveLength(3);
    });

    test('clicking a link scrolls to the matching section', () => {
        renderNavBar();

        const scrollIntoView = jest.fn();
        const target = document.createElement('div');
        target.id = 'overview';
        target.scrollIntoView = scrollIntoView;
        document.body.appendChild(target);

        fireEvent.click(screen.getByText('Overview'));

        expect(scrollIntoView).toHaveBeenCalledWith({
            behavior: 'smooth',
            block: 'start',
        });

        document.body.removeChild(target);
    });

    test('clicking a link does nothing when the target element is missing', () => {
        renderNavBar();

        expect(() => {
            fireEvent.click(screen.getByText('General Information'));
        }).not.toThrow();
    });
});
