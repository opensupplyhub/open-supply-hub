import React from 'react';
import { fireEvent } from '@testing-library/react';
import YearPicker from '../../components/FreeEmissionsEstimate/YearPicker';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('YearPicker component - Clear functionality', () => {
    const onChange = jest.fn();

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <YearPicker
                value="2024-01-01"
                onChange={onChange}
                placeholder="Select year"
                {...props}
            />,
        );

    beforeEach(() => {
        onChange.mockClear();
    });

    test('calls onChange with empty string when clear button is clicked', () => {
        const { getByLabelText } = renderComponent();

        const clearButton = getByLabelText('Clear year selection');
        fireEvent.click(clearButton);

        expect(onChange).toHaveBeenCalledWith('');
        expect(onChange).toHaveBeenCalledTimes(1);
    });

    test('does not render clear button when showClearButton is false', () => {
        const { queryByLabelText } = renderComponent({ showClearButton: false });

        const clearButton = queryByLabelText('Clear year selection');
        expect(clearButton).not.toBeInTheDocument();
    });
});

