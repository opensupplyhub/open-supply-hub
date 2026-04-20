import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityListsTable from '../../components/FacilityListsTable';

const makeList = (overrides = {}) => ({
    id: 1,
    name: 'Test List',
    description: 'A test list',
    file_name: 'test.csv',
    is_active: true,
    is_public: true,
    item_count: 10,
    items_url: '/api/facility-lists/1/items/',
    created_at: '2024-01-01T00:00:00Z',
    statuses: [],
    parsing_errors: [],
    match_responsibility: 'moderator',
    status_counts: {
        UPLOADED: 0,
        PARSED: 0,
        GEOCODED: 0,
        GEOCODED_NO_RESULTS: 0,
        MATCHED: 0,
        POTENTIAL_MATCH: 0,
        CONFIRMED_MATCH: 0,
        ERROR: 0,
        ERROR_PARSING: 0,
        ERROR_GEOCODING: 0,
        ERROR_MATCHING: 0,
        DELETED: 0,
        DUPLICATE: 0,
        ITEM_REMOVED: 0,
    },
    ...overrides,
});

const renderTable = lists =>
    renderWithProviders(
        <MemoryRouter>
            <FacilityListsTable facilityLists={lists} />
        </MemoryRouter>,
    );

describe('FacilityListsTable', () => {
    it('displays "Feedback Phase" when a list status is REJECTED', () => {
        renderTable([makeList({ status: 'REJECTED' })]);

        expect(screen.getByText('Feedback Phase')).toBeInTheDocument();
        expect(screen.queryByText('Rejected')).not.toBeInTheDocument();
    });

    it('displays "Replaced" when a list status is REPLACED', () => {
        renderTable([makeList({ status: 'REPLACED' })]);

        expect(screen.getByText('Replaced')).toBeInTheDocument();
        expect(screen.queryByText('Feedback Phase')).not.toBeInTheDocument();
    });

    it('displays "Pending approval" for a PENDING list with items beyond UPLOADED', () => {
        renderTable([
            makeList({
                status: 'PENDING',
                item_count: 5,
                status_counts: {
                    ...makeList().status_counts,
                    UPLOADED: 2,
                    PARSED: 3,
                },
            }),
        ]);

        expect(screen.getByText('Pending approval')).toBeInTheDocument();
    });
});
