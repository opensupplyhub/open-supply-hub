import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import UserProfileFacilityLists from '../../components/UserProfileFacilityLists/UserProfileFacilityLists';

const makeFacilityListsState = (overrides = {}) => ({
    profile: {
        facilityLists: {
            data: [],
            fetching: false,
            fetchingMore: false,
            nextPageUrl: null,
            error: null,
            ...overrides,
        },
    },
});

const renderComponent = (stateOverrides = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <UserProfileFacilityLists />
        </MemoryRouter>,
        { preloadedState: makeFacilityListsState(stateOverrides) },
    );

describe('UserProfileFacilityLists', () => {
    test('shows spinner when fetching', () => {
        const { getByRole } = renderComponent({ fetching: true });
        expect(getByRole('progressbar')).toBeInTheDocument();
    });

    test('shows error message', () => {
        const { getByText } = renderComponent({
            error: ['Something went wrong'],
        });
        expect(getByText('Something went wrong')).toBeInTheDocument();
    });

    test('renders nothing when list is empty', () => {
        const { container } = renderComponent({ data: [] });
        expect(container.firstChild).toBeNull();
    });

    test('renders facility list names', () => {
        const { getByText } = renderComponent({
            data: [
                {
                    id: 1,
                    name: 'My Test List',
                    description: 'A description',
                    contributor_id: 10,
                },
            ],
        });
        expect(getByText('My Test List')).toBeInTheDocument();
    });

    test('shows Load More button when nextPageUrl exists', () => {
        const { getByTestId } = renderComponent({
            data: [
                {
                    id: 1,
                    name: 'List A',
                    description: '',
                    contributor_id: 10,
                },
            ],
            nextPageUrl: '/api/facility-lists/?page=2',
        });
        expect(
            getByTestId('facility-lists-load-more'),
        ).toBeInTheDocument();
    });
});
