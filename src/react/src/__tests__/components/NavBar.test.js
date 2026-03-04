import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import NavBar from '../../components/ProductionLocation/Sidebar/NavBar/NavBar';

const renderNavBar = () =>
    renderWithProviders(
        <MemoryRouter>
            <NavBar />
        </MemoryRouter>,
    );

describe('NavBar', () => {
    test('renders the "Jump to" heading', () => {
        renderNavBar();

        expect(screen.getByText('Jump to')).toBeInTheDocument();
    });

    test('renders all three navigation items', () => {
        renderNavBar();

        expect(screen.getByText('Overview')).toBeInTheDocument();
        expect(screen.getByText('General Information')).toBeInTheDocument();
        expect(screen.getByText('Operational Details')).toBeInTheDocument();
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
