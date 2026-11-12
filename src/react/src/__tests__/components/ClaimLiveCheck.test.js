import React from 'react';
import { act, fireEvent } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimLiveCheck from '../../components/ClaimLiveCheck/ClaimLiveCheck';
import apiRequest from '../../util/apiRequest';
import {
    CHECK_TIMEOUT_MS,
    POLL_INTERVAL_MS,
    PROGRESS_LINE_INTERVAL_MS,
} from '../../components/ClaimLiveCheck/constants';

jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
    post: jest.fn(),
}));

const CLAIM_ID = 77;
const CHECK_URL = `/api/facility-claims/${CLAIM_ID}/live-check/`;
const STAY = 'Stay on this page. This takes up to one minute.';
const UNAVAILABLE = 'The pre-check is not available right now.';
const WORK_EMAIL = 'Use a work email, not a personal email.';
const COMPANY_ADDRESS =
    'Add an official document that shows the company address. For example a utility bill or business registration.';

const answer = (status, fixes = [], checksLeft = 2) => ({
    data: { status, fixes, checks_left: checksLeft },
});

const setReducedMotion = matches => {
    window.matchMedia = jest.fn(() => ({ matches }));
};

describe('ClaimLiveCheck component', () => {
    let history;

    const renderCheck = () =>
        renderWithProviders(
            <ClaimLiveCheck claimID={CLAIM_ID} history={history} />,
        );

    // Let the pending request promises settle.
    const settle = () => act(() => Promise.resolve());

    const advance = async ms => {
        await act(async () => {
            jest.advanceTimersByTime(ms);
        });
        await settle();
    };

    beforeEach(() => {
        jest.useFakeTimers();
        jest.clearAllMocks();
        history = { push: jest.fn() };
        setReducedMotion(false);
        apiRequest.post.mockResolvedValue(answer('CHECKING'));
        apiRequest.get.mockResolvedValue(answer('CHECKING'));
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    test('starts the check once and tells the claimant to stay', async () => {
        const { getByText } = renderCheck();

        expect(getByText('Checking your email.')).toBeInTheDocument();
        expect(getByText(STAY)).toBeInTheDocument();

        await settle();

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        expect(apiRequest.post).toHaveBeenCalledWith(CHECK_URL);
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('moves the progress line on while it waits', async () => {
        const { getByText } = renderCheck();
        await settle();

        await advance(PROGRESS_LINE_INTERVAL_MS);
        expect(getByText('Reading your documents.')).toBeInTheDocument();

        await advance(PROGRESS_LINE_INTERVAL_MS * 5);
        expect(
            getByText('Checking the company name and address.'),
        ).toBeInTheDocument();
    });

    test('polls while checking and stops at the answer', async () => {
        const { getByText, queryByText } = renderCheck();
        await settle();

        await advance(POLL_INTERVAL_MS);
        expect(apiRequest.get).toHaveBeenCalledTimes(1);
        expect(apiRequest.get).toHaveBeenCalledWith(CHECK_URL);
        expect(getByText(STAY)).toBeInTheDocument();

        apiRequest.get.mockResolvedValue(answer('PASSED', [], 0));
        await advance(POLL_INTERVAL_MS);

        expect(getByText('Your claim is approved.')).toBeInTheDocument();
        expect(queryByText(STAY)).toBeNull();

        await advance(POLL_INTERVAL_MS * 4);
        expect(apiRequest.get).toHaveBeenCalledTimes(2);
    });

    test('an approved claim celebrates and offers the ways out', async () => {
        apiRequest.post.mockResolvedValue(answer('PASSED', [], 0));
        const { getByText, getByTestId } = renderCheck();
        await settle();

        expect(getByText('Your claim is approved.')).toBeInTheDocument();
        expect(getByTestId('claim-live-check-confetti')).toHaveAttribute(
            'aria-hidden',
            'true',
        );

        fireEvent.click(getByText('To My Claims'));
        expect(history.push).toHaveBeenCalledWith('/claimed');
    });

    test('no confetti for people who prefer reduced motion', async () => {
        setReducedMotion(true);
        apiRequest.post.mockResolvedValue(answer('PASSED', [], 0));
        const { getByText, queryByTestId } = renderCheck();
        await settle();

        expect(getByText('Your claim is approved.')).toBeInTheDocument();
        expect(queryByTestId('claim-live-check-confetti')).toBeNull();
    });

    test('a claim that did not pass lists the preset fixes and two choices', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['work_email', 'company_address_document']),
        );
        const { getByText, getAllByRole } = renderCheck();
        await settle();

        expect(
            getByText('Your claim did not pass the pre-check.'),
        ).toBeInTheDocument();
        expect(getByText('Fix this:')).toBeInTheDocument();
        expect(
            getAllByRole('listitem').map(item => item.textContent),
        ).toEqual([WORK_EMAIL, COMPANY_ADDRESS]);
        expect(getByText('Choose one:')).toBeInTheDocument();
        expect(getByText('Go back and fix it')).toBeInTheDocument();
        expect(
            getByText('Opens the exact field to change. Then check again.'),
        ).toBeInTheDocument();
        expect(getByText('Leave it for review')).toBeInTheDocument();
        expect(
            getByText(
                'A person will review the claim. Approval can be significantly delayed.',
            ),
        ).toBeInTheDocument();
    });

    test('"Go back and fix it" opens the first fix on the edit page', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['work_email', 'company_address_document']),
        );
        const { getByText } = renderCheck();
        await settle();

        fireEvent.click(getByText('Go back and fix it'));

        expect(history.push).toHaveBeenCalledWith(
            `/claimed/pending/${CLAIM_ID}?fix=work_email&check=1`,
        );
    });

    test('with no checks left going back does not promise another check', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['upload_document'], 0),
        );
        const { getByText, queryByText } = renderCheck();
        await settle();

        expect(
            getByText('Opens the exact field to change.'),
        ).toBeInTheDocument();
        expect(queryByText(/Then check again/)).toBeNull();

        fireEvent.click(getByText('Go back and fix it'));
        expect(history.push).toHaveBeenCalledWith(
            `/claimed/pending/${CLAIM_ID}?fix=upload_document`,
        );
    });

    test('"Leave it for review" confirms the claim waits for a person', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['upload_document']),
        );
        const { getByText, queryByText } = renderCheck();
        await settle();

        fireEvent.click(getByText('Leave it for review'));

        expect(
            getByText('Your claim is waiting for a person to review it.'),
        ).toBeInTheDocument();
        expect(queryByText('Fix this:')).toBeNull();
        fireEvent.click(getByText('Search OS Hub'));
        expect(history.push).toHaveBeenCalledWith('/map');
    });

    test('an unknown fix is never shown', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['upload_document', 'Raw model text']),
        );
        const { getAllByRole, queryByText } = renderCheck();
        await settle();

        expect(getAllByRole('listitem')).toHaveLength(1);
        expect(queryByText(/Raw model text/)).toBeNull();
    });

    test('not passed with nothing to show reads as not available', async () => {
        apiRequest.post.mockResolvedValue(answer('NOT_PASSED', ['made_up']));
        const { getByText, queryByText } = renderCheck();
        await settle();

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        expect(queryByText('Fix this:')).toBeNull();
    });

    test('an unavailable check says the claim is submitted', async () => {
        apiRequest.post.mockResolvedValue(answer('UNAVAILABLE', [], 3));
        const { getByText } = renderCheck();
        await settle();

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        expect(
            getByText('Your claim is submitted. A person will review it.'),
        ).toBeInTheDocument();
        expect(getByText('To My Claims')).toBeInTheDocument();
    });

    test('a failed request to start the check fails open', async () => {
        apiRequest.post.mockRejectedValue(new Error('network'));
        const { getByText } = renderCheck();
        await settle();

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        await advance(POLL_INTERVAL_MS * 2);
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('a failed poll fails open', async () => {
        apiRequest.get.mockRejectedValue(new Error('network'));
        const { getByText } = renderCheck();
        await settle();

        await advance(POLL_INTERVAL_MS);

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
    });

    test('an unknown status reads as not available', async () => {
        apiRequest.post.mockResolvedValue(answer('SOMETHING_NEW'));
        const { getByText } = renderCheck();
        await settle();

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
    });

    test('gives up after one minute and stops asking', async () => {
        const { getByText, queryByText } = renderCheck();
        await settle();

        await advance(CHECK_TIMEOUT_MS - POLL_INTERVAL_MS);
        expect(getByText(STAY)).toBeInTheDocument();

        await advance(POLL_INTERVAL_MS);
        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        expect(queryByText(STAY)).toBeNull();

        const polls = apiRequest.get.mock.calls.length;
        await advance(POLL_INTERVAL_MS * 5);
        expect(apiRequest.get).toHaveBeenCalledTimes(polls);
    });

    test('stops asking and forgets the check when it is left', async () => {
        const { unmount, reduxStore } = renderCheck();
        await settle();
        await advance(POLL_INTERVAL_MS);
        const polls = apiRequest.get.mock.calls.length;

        unmount();
        await advance(POLL_INTERVAL_MS * 5);

        expect(apiRequest.get).toHaveBeenCalledTimes(polls);
        expect(reduxStore.getState().claimLiveCheck.claimID).toBeNull();
    });
});
