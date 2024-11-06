import React from 'react';
import { fireEvent } from '@testing-library/react';
import Table from '@material-ui/core/Table';
import DashboardModerationQueueListTableHeader from '../../components/Dashboard/DashboardModerationQueueListTableHeader';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { MODERATION_QUEUE_HEAD_CELLS } from '../../util/constants';

describe('DashboardModerationQueueListTableHeader component', () => {
    const mockOnRequestSort = jest.fn();
    const defaultProps = {
        order: 'asc',
        orderBy: 'name',
        onRequestSort: mockOnRequestSort,
        fetching: false,
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <Table>
                <DashboardModerationQueueListTableHeader {...defaultProps} {...props} />
            </Table>
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders all headers with sortable labels', () => {
        const { getByText } = renderComponent();

        MODERATION_QUEUE_HEAD_CELLS.forEach(({ label }) => {
            expect(getByText(label)).toBeInTheDocument();
        });
    });

    test('calls onRequestSort with correct arguments when a column is clicked', () => {
        const { getByText } = renderComponent();

        MODERATION_QUEUE_HEAD_CELLS.forEach(({ label }) => {
            const tableSortLabel = getByText(label);
            fireEvent.click(tableSortLabel);
        });

        expect(mockOnRequestSort).toHaveBeenCalledTimes(MODERATION_QUEUE_HEAD_CELLS.length);
    });

    test('disables sorting if fetching is true', () => {
        const { getAllByRole } = renderComponent({ fetching: true });

        const sortLabels = getAllByRole('button', { hidden: true });
        sortLabels.forEach(sortLabel => {
            expect(sortLabel).toHaveAttribute('tabindex', '-1');
        });
    });

    test('sets sort direction based on order and orderBy props', () => {
        const { getByText } = renderComponent({
            order: 'desc',
            orderBy: MODERATION_QUEUE_HEAD_CELLS[0].id,
        });

        const firstColumn = MODERATION_QUEUE_HEAD_CELLS[0];
        const headerCell = getByText(firstColumn.label).closest('th');

        expect(headerCell).toHaveAttribute('aria-sort', 'descending');
    });
});
