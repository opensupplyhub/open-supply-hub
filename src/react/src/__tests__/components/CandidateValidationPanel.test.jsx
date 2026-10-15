import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, fireEvent, waitFor, act } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import CandidateValidationPanel from '../../components/Candidate/CandidateValidationPanel';
import apiRequest from '../../util/apiRequest';
import { CANDIDATE_SLC_ENRICHMENT_ENABLED } from '../../util/candidateCopy';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
        post: jest.fn(),
    },
}));

const OS_ID = 'US2026ABCDEF1234';
const VOTES_URL = `/api/v1/production-locations/${OS_ID}/candidate-votes/`;
const DETAIL_URL = `/api/v1/production-locations/${OS_ID}/`;

const makeCandidate = (overrides = {}) => ({
    osId: OS_ID,
    source: 'Earth Genome',
    confidence: 0.87,
    externalId: 'eg-42',
    createdAt: null,
    coordinates: { lat: 35.1, lng: -79.1 },
    countryName: 'United States',
    suggestedMatches: [],
    isDetailLoaded: true,
    ...overrides,
    validation: {
        state: 'unverified',
        tally: { confirmed: 0, not_a_facility: 0 },
        yourVote: null,
        votingOpen: true,
        ...(overrides.validation || {}),
    },
});

const loggedIn = { auth: { user: { user: { isAnon: false, id: 7 } } } };
const anonymous = { auth: { user: { user: { isAnon: true, id: null } } } };
// Session check not finished: isAnon is not yet a boolean.
const sessionUnknown = { auth: { user: { user: { isAnon: undefined } } } };
// Session check in flight (auth.session.fetching) with the default user.
const sessionChecking = {
    auth: {
        user: { user: { isAnon: true, id: null } },
        session: { fetching: true },
    },
};

const renderPanel = (candidate, preloadedState = loggedIn, props = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <CandidateValidationPanel candidate={candidate} {...props} />
        </MemoryRouter>,
        { preloadedState },
    );

const resolvePost = (body, status = 201) =>
    apiRequest.post.mockResolvedValue({ data: body, status });

const rejectPost = status =>
    apiRequest.post.mockRejectedValue({ response: { status, data: {} } });

const confirmedButton = () => screen.getByTestId('candidate-vote-confirmed');
const notFacilityButton = () =>
    screen.getByTestId('candidate-vote-not-a-facility');

describe('CandidateValidationPanel', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the badge, provenance, state and tally', () => {
        renderPanel(
            makeCandidate({
                validation: {
                    tally: { confirmed: 1, not_a_facility: 0 },
                },
            }),
        );

        expect(screen.getByTestId('candidate-badge')).toHaveTextContent(
            'Satellite-detected candidate',
        );
        expect(screen.getByText(/Earth Genome/)).toBeInTheDocument();
        expect(screen.getByText(/87%/)).toBeInTheDocument();
        expect(screen.getByText(/eg-42/)).toBeInTheDocument();
        expect(screen.getByTestId('candidate-state-chip')).toHaveTextContent(
            'Unverified',
        );
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '1 say facility · 0 say not',
        );
    });

    it('posts a first vote, updates optimistically and reconciles', async () => {
        resolvePost(
            {
                os_id: OS_ID,
                your_vote: 'not_a_facility',
                tally: { confirmed: 2, not_a_facility: 1 },
                state: 'unverified',
            },
            201,
        );
        const onValidationChange = jest.fn();
        renderPanel(makeCandidate(), loggedIn, { onValidationChange });

        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            'No votes yet',
        );

        fireEvent.click(notFacilityButton());

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        expect(apiRequest.post).toHaveBeenCalledWith(VOTES_URL, {
            vote: 'not_a_facility',
        });
        // Optimistic update before the response arrives.
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '0 say facility · 1 say not',
        );
        expect(notFacilityButton()).toHaveAttribute('data-selected', 'true');

        await waitFor(() =>
            expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
                '2 say facility · 1 say not',
            ),
        );
        expect(notFacilityButton()).toHaveAttribute('aria-pressed', 'true');
        expect(confirmedButton()).toHaveAttribute('aria-pressed', 'false');
        expect(onValidationChange).toHaveBeenCalledWith(
            expect.objectContaining({
                state: 'unverified',
                yourVote: 'not_a_facility',
                tally: { confirmed: 2, not_a_facility: 1 },
            }),
        );
    });

    it('shows a returning user their vote and changes it in place', async () => {
        resolvePost(
            {
                os_id: OS_ID,
                your_vote: 'not_a_facility',
                tally: { confirmed: 0, not_a_facility: 1 },
                state: 'unverified',
            },
            200,
        );
        renderPanel(
            makeCandidate({
                validation: {
                    tally: { confirmed: 1, not_a_facility: 0 },
                    yourVote: 'confirmed',
                },
            }),
        );

        expect(confirmedButton()).toHaveAttribute('data-selected', 'true');
        expect(confirmedButton()).toHaveTextContent('Your vote');

        // Clicking the already-selected vote sends nothing.
        fireEvent.click(confirmedButton());
        expect(apiRequest.post).not.toHaveBeenCalled();

        fireEvent.click(notFacilityButton());

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        expect(apiRequest.post).toHaveBeenCalledWith(VOTES_URL, {
            vote: 'not_a_facility',
        });
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '0 say facility · 1 say not',
        );
        await waitFor(() =>
            expect(notFacilityButton()).toHaveAttribute(
                'data-selected',
                'true',
            ),
        );
        expect(confirmedButton()).toHaveAttribute('data-selected', 'false');
    });

    it('opens the login prompt for anonymous users without sending a request', () => {
        renderPanel(makeCandidate(), anonymous);

        expect(notFacilityButton()).not.toBeDisabled();
        fireEvent.click(notFacilityButton());

        expect(apiRequest.post).not.toHaveBeenCalled();
        expect(screen.getByTestId('candidate-login-dialog')).toBeInTheDocument();
        expect(screen.getByText('Log in to vote')).toBeInTheDocument();
        expect(
            screen.getByTestId('candidate-login-dialog-login'),
        ).toHaveAttribute('href', '/auth/login');
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            'No votes yet',
        );
    });

    it('renders the split for a disputed candidate', () => {
        renderPanel(
            makeCandidate({
                validation: {
                    state: 'disputed',
                    tally: { confirmed: 3, not_a_facility: 2 },
                },
            }),
        );

        expect(screen.getByTestId('candidate-state-chip')).toHaveTextContent(
            'Disputed',
        );
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '3 say facility · 2 say not',
        );
        expect(
            screen.getByText(/People disagree about this one/),
        ).toBeInTheDocument();
        expect(notFacilityButton()).not.toBeDisabled();
    });

    it('refetches the detail on 409 and applies the closed state and tally', async () => {
        rejectPost(409);
        apiRequest.get.mockResolvedValue({
            data: {
                os_id: OS_ID,
                is_candidate: true,
                validation: {
                    state: 'confirmed',
                    tally: { confirmed: 5, not_a_facility: 0 },
                    your_vote: null,
                    voting_open: false,
                },
            },
        });
        const onValidationChange = jest.fn();
        renderPanel(
            makeCandidate({
                validation: { tally: { confirmed: 4, not_a_facility: 0 } },
            }),
            loggedIn,
            { onValidationChange },
        );

        fireEvent.click(confirmedButton());

        await waitFor(() =>
            expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
                'Voting closed',
            ),
        );
        expect(apiRequest.get).toHaveBeenCalledWith(DETAIL_URL);
        expect(screen.getByTestId('candidate-state-chip')).toHaveTextContent(
            'Confirmed',
        );
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '5 say facility · 0 say not',
        );
        expect(confirmedButton()).toBeDisabled();
        expect(notFacilityButton()).toBeDisabled();
        expect(confirmedButton()).toHaveAttribute('data-selected', 'false');
        expect(onValidationChange).toHaveBeenCalledWith(
            expect.objectContaining({
                state: 'confirmed',
                votingOpen: false,
                tally: { confirmed: 5, not_a_facility: 0 },
            }),
        );
    });

    it('keeps the last known block closed when the 409 refetch fails', async () => {
        rejectPost(409);
        apiRequest.get.mockRejectedValue({ response: { status: 500 } });
        renderPanel(
            makeCandidate({
                validation: { tally: { confirmed: 4, not_a_facility: 0 } },
            }),
        );

        fireEvent.click(confirmedButton());

        await waitFor(() =>
            expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
                'Voting closed',
            ),
        );
        expect(confirmedButton()).toBeDisabled();
        expect(notFacilityButton()).toBeDisabled();
        // The optimistic change was rolled back.
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '4 say facility · 0 say not',
        );
        expect(screen.getByTestId('candidate-state-chip')).toHaveTextContent(
            'Unverified',
        );
    });

    it('disables voting with "Checking your session…" until the session is known', () => {
        renderPanel(makeCandidate(), sessionUnknown);

        expect(confirmedButton()).toBeDisabled();
        expect(notFacilityButton()).toBeDisabled();
        expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
            'Checking your session',
        );
        fireEvent.click(notFacilityButton());
        expect(apiRequest.post).not.toHaveBeenCalled();
        expect(
            screen.queryByTestId('candidate-login-dialog'),
        ).not.toBeInTheDocument();
    });

    it('treats an in-flight session check the same way', () => {
        renderPanel(makeCandidate(), sessionChecking);

        expect(confirmedButton()).toBeDisabled();
        expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
            'Checking your session',
        );
        expect(
            screen.queryByTestId('candidate-login-dialog'),
        ).not.toBeInTheDocument();
    });

    it('announces status changes through a polite live region', () => {
        renderPanel(makeCandidate());

        const region = screen.getByTestId('candidate-vote-status-region');
        expect(region).toHaveAttribute('aria-live', 'polite');
        expect(region).toContainElement(
            screen.getByTestId('candidate-vote-status'),
        );
    });

    it('moves focus to the heading when opened as an overlay', () => {
        renderPanel(makeCandidate(), loggedIn, {
            variant: 'overlay',
            onClose: jest.fn(),
        });

        expect(
            screen.getByRole('heading', { name: 'Is there a facility here?' }),
        ).toHaveFocus();
    });

    it('does not steal focus when rendered inline', () => {
        renderPanel(makeCandidate(), loggedIn, { variant: 'inline' });

        expect(
            screen.getByRole('heading', { name: 'Is there a facility here?' }),
        ).not.toHaveFocus();
    });

    it('renders confirmed candidates as closed without a request', () => {
        renderPanel(
            makeCandidate({
                validation: {
                    state: 'confirmed',
                    tally: { confirmed: 5, not_a_facility: 0 },
                    votingOpen: false,
                },
            }),
        );

        expect(confirmedButton()).toBeDisabled();
        expect(notFacilityButton()).toBeDisabled();
        expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
            'Voting closed',
        );
        fireEvent.click(notFacilityButton());
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    it('explains a retired candidate when the server answers 410', async () => {
        rejectPost(410);
        renderPanel(makeCandidate());

        fireEvent.click(notFacilityButton());

        await waitFor(() =>
            expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
                'This candidate was retired',
            ),
        );
        expect(notFacilityButton()).toBeDisabled();
    });

    it('rolls back and shows a retry message on other errors', async () => {
        rejectPost(500);
        renderPanel(makeCandidate());

        fireEvent.click(confirmedButton());
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            '1 say facility · 0 say not',
        );

        await waitFor(() =>
            expect(screen.getByTestId('candidate-vote-status')).toHaveTextContent(
                'could not be saved',
            ),
        );
        expect(screen.getByTestId('candidate-tally')).toHaveTextContent(
            'No votes yet',
        );
        expect(confirmedButton()).not.toBeDisabled();
    });

    it('lists suggested matches with links', () => {
        renderPanel(
            makeCandidate({
                suggestedMatches: [
                    {
                        osId: 'US2020XYZ',
                        name: 'Nearby Farm',
                        address: '1 Farm Rd',
                        distanceM: 240,
                    },
                ],
            }),
        );

        const link = screen.getByTestId('candidate-match-link');
        expect(link).toHaveTextContent('Nearby Farm');
        expect(link).toHaveAttribute('href', '/facilities/US2020XYZ');
        expect(screen.getByText('1 Farm Rd · 240 m')).toBeInTheDocument();
    });

    it('hides "I know this facility" while SLC enrichment is disabled', () => {
        expect(CANDIDATE_SLC_ENRICHMENT_ENABLED).toBe(false);
        renderPanel(makeCandidate());

        expect(
            screen.queryByTestId('candidate-know-this-facility'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByText('I know this facility'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByText(/Add a name and address/),
        ).not.toBeInTheDocument();
    });

    it('links "I know this facility" into the SLC update flow when enabled', () => {
        renderPanel(makeCandidate(), loggedIn, { slcEnrichmentEnabled: true });

        expect(
            screen.getByTestId('candidate-know-this-facility'),
        ).toHaveAttribute('href', `/contribute/single-location/${OS_ID}/info/`);
        expect(
            screen.getByText(/Add a name and address/),
        ).toBeInTheDocument();
    });

    it('fetches the detail for a layer seed and applies your_vote', async () => {
        apiRequest.get.mockResolvedValue({
            data: {
                os_id: OS_ID,
                is_candidate: true,
                source: 'Earth Genome',
                confidence: 0.87,
                external_id: 'eg-42',
                validation: {
                    state: 'unverified',
                    tally: { confirmed: 1, not_a_facility: 0 },
                    your_vote: 'confirmed',
                    voting_open: true,
                },
                suggested_matches: [],
            },
        });
        const seed = makeCandidate({
            externalId: null,
            isDetailLoaded: false,
            validation: { tally: { confirmed: 1, not_a_facility: 0 } },
        });
        delete seed.validation.yourVote;

        await act(async () => {
            renderPanel(seed);
        });

        expect(apiRequest.get).toHaveBeenCalledWith(
            `/api/v1/production-locations/${OS_ID}/`,
            expect.objectContaining({ signal: expect.anything() }),
        );
        await waitFor(() =>
            expect(confirmedButton()).toHaveAttribute('data-selected', 'true'),
        );
        expect(screen.getByText(/eg-42/)).toBeInTheDocument();
    });
});
