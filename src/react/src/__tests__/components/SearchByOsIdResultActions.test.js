import React from 'react';
import { fireEvent } from '@testing-library/react';
import SearchByOsIdResultActions from '../../components/Contribute/SearchByOsIdResultActions';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('SearchByOsIdResultActions component', () => {
    const defaultButtonAction = jest.fn();
    const secondaryButtonAction = jest.fn();
    const defaultProps = {
        defaultButtonLabel: 'Default Button',
        defaultButtonAction,
        secondaryButtonLabel: 'Secondary Button',
        secondaryButtonAction,
    };

    it('renders without crashing', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdResultActions {...defaultProps}/>);

        expect(getByText('Default Button')).toBeInTheDocument();
        expect(getByText('Secondary Button')).toBeInTheDocument();
    });

    it('calls the defaultButtonAction function when clicked', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdResultActions {...defaultProps}/>);

        fireEvent.click(getByText('Default Button'));

        expect(defaultButtonAction).toHaveBeenCalledTimes(1);
    });

    it('calls the secondaryButtonAction function when clicked', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdResultActions {...defaultProps}/>);

        fireEvent.click(getByText('Secondary Button'));

        expect(secondaryButtonAction).toHaveBeenCalledTimes(1);
    });
});