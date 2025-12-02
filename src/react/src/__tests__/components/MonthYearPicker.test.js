import React from 'react';
import { fireEvent } from '@testing-library/react';
import MonthYearPicker from '../../components/FreeEmissionsEstimate/MonthYearPicker';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('MonthYearPicker component - Clear functionality', () => {
    const onChange = jest.fn();

    const renderComponent = () =>
        renderWithProviders(
            <MonthYearPicker
                label="Closing Date"
                tooltipText="Enter the closing date"
                value="2024-06-01"
                onChange={onChange}
                placeholderMonth="Select month"
                placeholderYear="Select year"
            />,
        );

    beforeEach(() => {
        onChange.mockClear();
    });

    test('calls onChange with empty string when clear button is clicked', () => {
        const { getByLabelText } = renderComponent();

        const clearButton = getByLabelText('Clear date selection');
        fireEvent.click(clearButton);

        expect(onChange).toHaveBeenCalledWith('');
        expect(onChange).toHaveBeenCalledTimes(1);
    });

    test('YearPicker inside MonthYearPicker does not show its own clear button', () => {
        const { queryByLabelText } = renderComponent();

        // Should only find one clear button (from MonthYearPicker, not from YearPicker).
        const clearButtons = queryByLabelText('Clear year selection');
        expect(clearButtons).not.toBeInTheDocument();
    });
});

