import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import DashboardDeleteFacilityControls from '../../components/DashboardDeleteFacilityControls';

jest.mock('react-toastify', () => ({
    toast: jest.fn(),
}));

const defaultData = {
    id: 'CN2021250B1GHZ8',
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.3, 39.9] },
    properties: {
        name: 'Test Facility',
        address: '123 Test St',
        country_name: 'China',
        country_code: 'CN',
    },
};

const renderComponent = props =>
    render(
        <DashboardDeleteFacilityControls
            handleDelete={jest.fn()}
            deleting={false}
            error={null}
            disabled={false}
            data={defaultData}
            {...props}
        />,
    );

describe('DashboardDeleteFacilityControls', () => {
    test('renders without crashing', () => {
        renderComponent();
    });

    test('shows the Delete facility button', () => {
        const { getAllByText } = renderComponent();
        expect(getAllByText('Delete facility').length).toBeGreaterThan(0);
    });

    test('does not show an error message when error is null', () => {
        const { queryByRole } = renderComponent({ error: null });
        expect(queryByRole('generic', { name: /error/i })).toBeNull();
    });

    test('displays API error message when error array is provided', () => {
        const { getByText } = renderComponent({
            error: ['Facilities with approved claims cannot be deleted'],
        });
        expect(
            getByText('Facilities with approved claims cannot be deleted'),
        ).toBeInTheDocument();
    });

    test('joins multiple error messages with a comma and space', () => {
        const { getByText } = renderComponent({
            error: ['First error', 'Second error'],
        });
        expect(getByText('First error, Second error')).toBeInTheDocument();
    });

    test('shows a spinner and no dialog when deleting', () => {
        const { queryByText } = renderComponent({ deleting: true });
        expect(queryByText('Do you really want to delete this facility?')).toBeNull();
    });

    test('opens confirmation dialog when Delete facility button is clicked', async () => {
        const { getAllByText, getByText } = renderComponent();
        fireEvent.click(getAllByText('Delete facility')[0]);
        await waitFor(() => {
            expect(
                getByText('Do you really want to delete this facility?'),
            ).toBeInTheDocument();
        });
    });

    test('closes the dialog when Cancel is clicked', async () => {
        const { getAllByText, getByText, queryByText } = renderComponent();
        fireEvent.click(getAllByText('Delete facility')[0]);
        await waitFor(() =>
            expect(
                getByText('Do you really want to delete this facility?'),
            ).toBeInTheDocument(),
        );
        fireEvent.click(getByText('Cancel'));
        await waitFor(() => {
            expect(
                queryByText('Do you really want to delete this facility?'),
            ).toBeNull();
        });
    });

    test('calls handleDelete when deletion is confirmed', async () => {
        const handleDelete = jest.fn();
        const { getAllByText } = renderComponent({ handleDelete });
        fireEvent.click(getAllByText('Delete facility')[0]);
        await waitFor(() =>
            expect(getAllByText('Delete facility').length).toBeGreaterThan(1),
        );
        fireEvent.click(getAllByText('Delete facility')[1]);
        expect(handleDelete).toHaveBeenCalledTimes(1);
    });

    test('disables the button when disabled prop is true', () => {
        const { getAllByText } = renderComponent({ disabled: true });
        expect(getAllByText('Delete facility')[0].closest('button')).toBeDisabled();
    });

    test('disables the button when deleting is true', () => {
        const { getAllByText } = renderComponent({ deleting: true });
        expect(getAllByText('Delete facility')[0].closest('button')).toBeDisabled();
    });
});
