import React from 'react';
import { MemoryRouter, Route } from 'react-router-dom';
import { screen, fireEvent, waitFor, within } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import CandidateReviewPage from '../../components/Candidate/CandidateReviewPage';
import apiRequest from '../../util/apiRequest';
import { candidatesRoute } from '../../util/constants';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
        post: jest.fn(),
    },
}));

// Leaflet needs a real DOM layout; the map's contract with the page is
// three callbacks, exercised here through a stub.
jest.mock('../../components/Candidate/CandidateListMap', () => ({
    __esModule: true,
    default: ({ rows, selectedOsId, bbox, onSelect, onBboxChange }) => (
        <div
            data-testid="mock-map"
            data-count={rows.length}
            data-selected={selectedOsId || ''}
            data-bbox={bbox || ''}
        >
            <button
                type="button"
                data-testid="mock-map-draw"
                onClick={() => onBboxChange('-87.5,33.5,-86.5,34.5')}
            >
                draw
            </button>
            <button
                type="button"
                data-testid="mock-map-clear"
                onClick={() => onBboxChange(null)}
            >
                clear
            </button>
            {rows.map(row => (
                <button
                    type="button"
                    key={row.osId}
                    data-testid={`mock-map-dot-${row.osId}`}
                    onClick={() => onSelect(row.osId)}
                >
                    {row.osId}
                </button>
            ))}
        </div>
    ),
}));

const LIST_URL = '/api/v1/production-locations/candidates/';

const feature = (osId, overrides = {}) => ({
    type: 'Feature',
    id: osId,
    geometry: { type: 'Point', coordinates: [-86.9, 33.7] },
    properties: {
        os_id: osId,
        confidence: 0.42,
        source: 'earth_genome',
        state: 'unverified',
        tally: { confirmed: 0, not_a_facility: 0 },
        centroid: { lat: 33.7, lng: -86.9 },
        nearby_count: 0,
        nearest_m: null,
        nearest: null,
        created_at: '2026-11-04T10:00:00Z',
        country_code: 'US',
        external_id: `AL${osId.slice(-3)}`,
        ...overrides,
    },
});

const ROWS = [
    feature('US2026308AAAAAA'),
    feature('US2026308BBBBBB', {
        confidence: 0.91,
        nearby_count: 1,
        nearest_m: 388.2,
        nearest: {
            os_id: 'US2025292ABCDEF',
            name: 'Example Processing Plant',
            distance_m: 388.2,
        },
    }),
    feature('US2026308CCCCCC', {
        state: 'disputed',
        tally: { confirmed: 2, not_a_facility: 2 },
    }),
];

const listBody = (features = ROWS, count = features.length) => ({
    type: 'FeatureCollection',
    count,
    next: null,
    previous: null,
    features,
});

const detailBody = osId => ({
    os_id: osId,
    is_candidate: true,
    source: 'earth_genome',
    confidence: 0.42,
    external_id: 'AL001',
    created_at: '2026-11-04T10:00:00Z',
    coordinates: { lat: 33.7, lng: -86.9 },
    country: { alpha_2: 'US', name: 'United States' },
    validation: {
        state: 'unverified',
        tally: { confirmed: 0, not_a_facility: 0 },
        your_vote: null,
        voting_open: true,
    },
    suggested_matches: [],
});

const loggedIn = { auth: { user: { user: { isAnon: false, id: 7 } } } };
const anonymous = { auth: { user: { user: { isAnon: true, id: null } } } };

const mockApi = (body = listBody()) => {
    apiRequest.get.mockImplementation(url => {
        if (url.startsWith(LIST_URL)) {
            return Promise.resolve({ data: body });
        }
        const osId = url.split('/').filter(Boolean).pop();
        return Promise.resolve({ data: detailBody(osId) });
    });
};

const listRequests = () =>
    apiRequest.get.mock.calls
        .map(([url]) => url)
        .filter(url => url.startsWith(LIST_URL));

const lastListRequest = () => {
    const urls = listRequests();
    return urls[urls.length - 1];
};

const renderPage = (preloadedState = loggedIn, search = '') =>
    renderWithProviders(
        <MemoryRouter initialEntries={[`${candidatesRoute}${search}`]}>
            <Route path={candidatesRoute} component={CandidateReviewPage} />
        </MemoryRouter>,
        { preloadedState },
    );

const rows = () => screen.getAllByTestId('candidate-list-row');

describe('CandidateReviewPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('lists the first page with linked OS IDs and the list-only columns', async () => {
        mockApi();
        renderPage();

        await waitFor(() => expect(rows()).toHaveLength(3));
        expect(lastListRequest()).toBe(`${LIST_URL}?page=1&limit=50`);

        const links = screen.getAllByTestId('candidate-os-id-link');
        expect(links[0]).toHaveAttribute(
            'href',
            '/facilities/US2026308AAAAAA',
        );
        expect(screen.getByTestId('candidate-nearest-link')).toHaveAttribute(
            'href',
            '/facilities/US2025292ABCDEF',
        );
        expect(screen.getByText('388 m')).toBeInTheDocument();
        expect(screen.getByText('2 say facility · 2 say not')).toBeInTheDocument();
        expect(screen.getByTestId('candidate-list-summary')).toHaveTextContent(
            '3 detections · page 1 of 1',
        );
        expect(screen.getByTestId('mock-map')).toHaveAttribute(
            'data-count',
            '3',
        );
        expect(document.head.querySelector('meta[name="robots"]')).toHaveAttribute(
            'content',
            'noindex',
        );
    });

    it('reads the query from the URL and refetches when filters change', async () => {
        mockApi();
        renderPage(loggedIn, '?sort=-confidence&state=disputed&page=2');

        await waitFor(() => expect(listRequests()).toHaveLength(1));
        expect(lastListRequest()).toBe(
            `${LIST_URL}?page=2&limit=50&sort=-confidence&state=disputed`,
        );

        // Adding a state goes back to page 1.
        fireEvent.click(screen.getByTestId('candidate-filter-state-unverified'));
        await waitFor(() => expect(listRequests()).toHaveLength(2));
        expect(lastListRequest()).toBe(
            `${LIST_URL}?page=1&limit=50&sort=-confidence&state=disputed%2Cunverified`,
        );

        // Nearby is a Select: open it and pick an option from the menu.
        fireEvent.click(screen.getByTestId('candidate-filter-nearby'));
        fireEvent.click(await screen.findByText('Has one'));
        await waitFor(() =>
            expect(lastListRequest()).toContain('has_nearby=true'),
        );

        const min = screen.getByTestId('candidate-filter-confidence-min');
        // Unparseable text commits as "no filter", which is what the
        // field already held, so the field must not keep showing it.
        const requestsBefore = apiRequest.get.mock.calls.length;
        fireEvent.change(min, { target: { value: 'abc' } });
        fireEvent.blur(min);
        await waitFor(() => expect(min.value).toBe(''));
        expect(apiRequest.get.mock.calls.length).toBe(requestsBefore);

        fireEvent.change(min, { target: { value: '25' } });
        fireEvent.blur(min);
        await waitFor(() =>
            expect(lastListRequest()).toContain('confidence_min=0.25'),
        );

        const country = screen.getByTestId('candidate-filter-country');
        fireEvent.change(country, { target: { value: 'us, mx' } });
        fireEvent.keyDown(country, { key: 'Enter' });
        await waitFor(() =>
            expect(lastListRequest()).toContain('country=US%2CMX'),
        );
        // Re-typing the same codes in lower case normalises to the value
        // already applied; the field shows the applied form.
        fireEvent.change(country, { target: { value: 'us,mx' } });
        fireEvent.blur(country);
        await waitFor(() => expect(country.value).toBe('US,MX'));
        // A three-letter code is not a filter the API accepts; it is
        // dropped (clearing the filter) rather than sent as a 400.
        fireEvent.change(country, { target: { value: 'USA' } });
        fireEvent.blur(country);
        await waitFor(() =>
            expect(lastListRequest()).not.toContain('country='),
        );
        expect(country.value).toBe('');

        // A maximum below the applied minimum (25) is an inverted range
        // the API refuses; it is dropped and the field re-reads the
        // applied value.
        const max = screen.getByTestId('candidate-filter-confidence-max');
        const requestsBeforeMax = apiRequest.get.mock.calls.length;
        fireEvent.change(max, { target: { value: '10' } });
        fireEvent.blur(max);
        await waitFor(() => expect(max.value).toBe(''));
        expect(apiRequest.get.mock.calls.length).toBe(requestsBeforeMax);
        expect(lastListRequest()).not.toContain('confidence_max');

        fireEvent.click(screen.getByTestId('candidate-filter-reset'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(
                `${LIST_URL}?page=1&limit=50&sort=-confidence`,
            ),
        );
    });

    it('sorts from the table headers: natural direction first, then flipped', async () => {
        mockApi();
        renderPage();
        await waitFor(() => expect(rows()).toHaveLength(3));

        fireEvent.click(screen.getByTestId('candidate-sort-confidence'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(`${LIST_URL}?page=1&limit=50&sort=confidence`),
        );
        fireEvent.click(screen.getByTestId('candidate-sort-confidence'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(
                `${LIST_URL}?page=1&limit=50&sort=-confidence`,
            ),
        );
        fireEvent.click(screen.getByTestId('candidate-sort-nearby_count'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(
                `${LIST_URL}?page=1&limit=50&sort=-nearby_count`,
            ),
        );
    });

    it('pages through the list', async () => {
        mockApi(listBody(ROWS, 120));
        renderPage();
        await waitFor(() => expect(rows()).toHaveLength(3));
        expect(screen.getByTestId('candidate-list-summary')).toHaveTextContent(
            '120 detections · page 1 of 3',
        );

        fireEvent.click(screen.getByLabelText('Next page'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(`${LIST_URL}?page=2&limit=50`),
        );
        await waitFor(() =>
            expect(
                screen.getByTestId('candidate-list-summary'),
            ).toHaveTextContent('page 2 of 3'),
        );
    });

    it('offers the first page when the requested page is past the end', async () => {
        apiRequest.get.mockRejectedValue({ response: { status: 404 } });
        renderPage(loggedIn, '?page=9');

        await waitFor(() =>
            expect(screen.getByTestId('candidate-list-first-page')).toBeInTheDocument(),
        );
        mockApi();
        fireEvent.click(screen.getByTestId('candidate-list-first-page'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(`${LIST_URL}?page=1&limit=50`),
        );
    });

    it('opens the panel for a row, votes in place and steps to the next row', async () => {
        mockApi();
        apiRequest.post.mockResolvedValue({
            status: 201,
            data: {
                os_id: 'US2026308AAAAAA',
                your_vote: 'not_a_facility',
                tally: { confirmed: 0, not_a_facility: 1 },
                state: 'unverified',
            },
        });
        renderPage();
        await waitFor(() => expect(rows()).toHaveLength(3));

        fireEvent.click(rows()[0]);
        const panel = await screen.findByTestId('candidate-validation-panel');
        expect(panel).toHaveAttribute('data-os-id', 'US2026308AAAAAA');
        expect(screen.getByTestId('candidate-panel-position')).toHaveTextContent(
            '1 of 3 on this page',
        );
        expect(screen.getByTestId('candidate-panel-previous')).toBeDisabled();
        // The panel fetched the detail for your_vote and suggestions.
        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                '/api/v1/production-locations/US2026308AAAAAA/',
                expect.anything(),
            ),
        );

        fireEvent.click(screen.getByTestId('candidate-vote-not-a-facility'));
        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/v1/production-locations/US2026308AAAAAA/candidate-votes/',
                { vote: 'not_a_facility' },
            ),
        );
        // The row reflects the vote without a list refetch.
        await waitFor(() =>
            expect(
                within(rows()[0]).getByTestId('candidate-row-tally'),
            ).toHaveTextContent('0 say facility · 1 say not'),
        );
        expect(listRequests()).toHaveLength(1);

        fireEvent.click(screen.getByTestId('candidate-panel-next'));
        await waitFor(() =>
            expect(
                screen.getByTestId('candidate-validation-panel'),
            ).toHaveAttribute('data-os-id', 'US2026308BBBBBB'),
        );
        expect(screen.getByTestId('candidate-panel-position')).toHaveTextContent(
            '2 of 3 on this page',
        );
        expect(rows()[1]).toHaveAttribute('aria-selected', 'true');

        fireEvent.click(screen.getByTestId('candidate-panel-next'));
        await waitFor(() =>
            expect(screen.getByTestId('candidate-panel-next')).toBeDisabled(),
        );

        fireEvent.click(screen.getByTestId('candidate-panel-close'));
        await waitFor(() =>
            expect(
                screen.queryByTestId('candidate-validation-panel'),
            ).not.toBeInTheDocument(),
        );
    });

    it('selects a row from the map and clears the selection when the page changes', async () => {
        mockApi(listBody(ROWS, 120));
        renderPage();
        await waitFor(() => expect(rows()).toHaveLength(3));

        fireEvent.click(screen.getByTestId('mock-map-dot-US2026308CCCCCC'));
        await waitFor(() =>
            expect(screen.getByTestId('mock-map')).toHaveAttribute(
                'data-selected',
                'US2026308CCCCCC',
            ),
        );
        fireEvent.click(screen.getByLabelText('Next page'));
        await waitFor(() =>
            expect(
                screen.queryByTestId('candidate-validation-panel'),
            ).not.toBeInTheDocument(),
        );
    });

    it('limits the list to an area drawn on the map and can clear it', async () => {
        mockApi();
        renderPage();
        await waitFor(() => expect(rows()).toHaveLength(3));

        fireEvent.click(screen.getByTestId('mock-map-draw'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(
                `${LIST_URL}?page=1&limit=50&bbox=-87.5%2C33.5%2C-86.5%2C34.5`,
            ),
        );
        expect(screen.getByTestId('candidate-filter-area-chip')).toBeInTheDocument();
        expect(screen.getByTestId('mock-map')).toHaveAttribute(
            'data-bbox',
            '-87.5,33.5,-86.5,34.5',
        );

        fireEvent.click(screen.getByTestId('mock-map-clear'));
        await waitFor(() =>
            expect(lastListRequest()).toBe(`${LIST_URL}?page=1&limit=50`),
        );
        expect(
            screen.queryByTestId('candidate-filter-area-chip'),
        ).not.toBeInTheDocument();
    });

    it('shows the empty state when nothing matches', async () => {
        mockApi(listBody([], 0));
        renderPage();

        expect(await screen.findByTestId('candidate-list-empty')).toBeInTheDocument();
        expect(screen.queryByTestId('candidate-list-table')).not.toBeInTheDocument();
    });

    it('shows the login prompt to a logged-out visitor and requests nothing', async () => {
        mockApi();
        renderPage(anonymous);

        expect(await screen.findByTestId('candidate-login-dialog')).toBeInTheDocument();
        expect(screen.getByTestId('candidate-review-login-note')).toBeInTheDocument();
        expect(screen.queryByTestId('candidate-list-table')).not.toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    it('waits for the session check before requesting anything', () => {
        mockApi();
        renderPage({ auth: { user: { user: { isAnon: undefined } } } });

        expect(screen.queryByTestId('candidate-list-table')).not.toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });
});
