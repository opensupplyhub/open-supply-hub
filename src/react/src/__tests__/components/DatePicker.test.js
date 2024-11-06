import React from 'react';
import { fireEvent } from '@testing-library/react';
import DatePicker from '../../components/DatePicker';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('DatePicker component', () => {
    const label = 'Select Date';
    const value = '2024-10-25';
    const onChange = jest.fn();
    const name = 'testDate';

    const renderComponent = () =>
        renderWithProviders(
            <DatePicker
                label={label}
                value={value}
                onChange={onChange}
                name={name}
            />
        );

    test('renders DatePicker with label and TextField', () => {
        const { getByText, getByDisplayValue } = renderComponent();

        expect(getByText(label)).toBeInTheDocument();

        const input = getByDisplayValue(value);
        expect(input).toBeInTheDocument();
        expect(input).toHaveAttribute('type', 'date');
        expect(input).toHaveAttribute('id', name);
    });

    test('calls onChange function when date is changed', () => {
        const { getByDisplayValue } = renderComponent();
        const newDate = '2024-11-01';

        const input = getByDisplayValue(value);
        fireEvent.change(input, { target: { value: newDate } });

        expect(onChange).toHaveBeenCalledWith(newDate);
    });
});
