import React from 'react';
import { fireEvent } from '@testing-library/react';
import BackToSearchButton from '../../components/Contribute/BackToSearchButton';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('BackToSearchButton component', () => {
    const handleBackToSearch = jest.fn();
    const defaultProps = {
        label: 'Back to ID search',
        handleBackToSearch,
    };

    it('renders the button with the correct label', () => {
        const { getByText } = renderWithProviders(<BackToSearchButton {...defaultProps} />);

        expect(getByText('Back to ID search')).toBeInTheDocument();
    });

    it('calls the handleBackToSearch function when clicked', () => {
        const { getByText } = renderWithProviders(<BackToSearchButton {...defaultProps} />);

        fireEvent.click(getByText('Back to ID search'));

        expect(handleBackToSearch).toHaveBeenCalledTimes(1);
    });
});