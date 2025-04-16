import React from 'react';
import { fireEvent } from '@testing-library/react';
import { Router } from 'react-router-dom';
import SearchByOsIdTab from '../../components/Contribute/SearchByOsIdTab';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import history from '../../util/history';


describe('SearchByOsIdTab component', () => {

    it('renders without crashing', () => {
        const { getByText, getByPlaceholderText, getByRole } = renderWithProviders(<SearchByOsIdTab />);
        expect(
            getByText(
                'Enter the full OS ID to search for a matching profile. Use the field below and click “search”.'
            )
        ).toBeInTheDocument();
        expect(
            getByText('Know the OS ID for your location?')
        ).toBeInTheDocument();
        expect(
            getByText(
                'If you know the OS ID for your production location enter it below, otherwise select the “Search by Name and Address” tab.'
            )
        ).toBeInTheDocument();
        expect(getByPlaceholderText('Enter the OS ID')).toBeInTheDocument();
        expect(getByText(
            'To search by ID, you need to enter the full OS ID of the production location.'
        )).toBeInTheDocument();
        
        const button = getByRole('button', { name: /Search by ID/i });
        expect(button).toBeDisabled();
    });

    it('allows the user to enter a value and disables the button if input length is less than 15', () => {
        const { getByPlaceholderText, getByRole } = renderWithProviders(<SearchByOsIdTab />);
        const input = getByPlaceholderText('Enter the OS ID');

        fireEvent.change(input, { target: { value: 'CN2021250D1DTN' } });

        const button = getByRole('button', { name: /Search by ID/i });
        expect(button).toBeDisabled();
    });

    it('enables the search button when the OS ID length is 15', () => {
        const { getByPlaceholderText, getByRole } = renderWithProviders(<SearchByOsIdTab />);
        const input = getByPlaceholderText('Enter the OS ID');

        fireEvent.change(input, { target: { value: 'CN2021250D1DTN7' } });

        const button = getByRole('button', { name: /Search by ID/i });
        expect(button).not.toBeDisabled();
    });

    it('navigates to the correct URL when the search button is clicked with valid input', () => {
        const { getByPlaceholderText, getByRole } = renderWithProviders(
            <Router history={history}>
                <SearchByOsIdTab />
            </Router>
        );
        const input = getByPlaceholderText('Enter the OS ID');

        fireEvent.change(input, { target: { value: 'CN2021250D1DTN7' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1DTN7'
        );
    });

    it('should replace special characters in the URL with their encoded values', () => {
        const { getByPlaceholderText, getByRole } = renderWithProviders(
            <Router history={history}>
                <SearchByOsIdTab />
            </Router>
        );
        const input = getByPlaceholderText('Enter the OS ID');

        fireEvent.change(input, { target: { value: 'CN2021250D1D/TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%2FTN'
        );

        fireEvent.change(input, { target: { value: 'CN2021250D1D?TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%3FTN'
        );

        fireEvent.change(input, { target: { value: 'CN2021250D1D#TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%23TN'
        );

        fireEvent.change(input, { target: { value: 'CN2021250D1D$TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));    

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%24TN'
        );

        fireEvent.change(input, { target: { value: 'CN2021250D1D&TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%26TN'
        );

        fireEvent.change(input, { target: { value: 'CN2021250D1D@TN' } });
        fireEvent.click(getByRole('button', { name: /Search by ID/i }));

        expect(history.location.pathname).toBe(
            '/contribute/single-location/search/id/CN2021250D1D%40TN'
        );
    });

    it('transforms input to uppercase when typing', () => {
        const { getByPlaceholderText } = renderWithProviders(<SearchByOsIdTab />);
        const input = getByPlaceholderText('Enter the OS ID');

        fireEvent.change(input, { target: { value: 'abcd123' } });

        expect(input.value).toBe('ABCD123'); 
    });
});
