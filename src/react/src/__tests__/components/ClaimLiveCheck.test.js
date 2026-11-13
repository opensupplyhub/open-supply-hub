import React from 'react';
import { act, cleanup, fireEvent } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimLiveCheck from '../../components/ClaimLiveCheck/ClaimLiveCheck';
import apiRequest from '../../util/apiRequest';
import {
    CHECK_TIMEOUT_MS,
    FACT_INTERVAL_MS,
    POLL_INTERVAL_MS,
    RESULT_HOLD_MS,
} from '../../components/ClaimLiveCheck/constants';

jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
    post: jest.fn(),
}));

const CLAIM_ID = 77;
const CHECK_URL = `/api/facility-claims/${CLAIM_ID}/live-check/`;
const STAY = 'This takes up to one minute. Stay on this page.';
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

    let now;

    const renderCheck = (location = {}, props = {}) =>
        renderWithProviders(
            <ClaimLiveCheck
                claimID={CLAIM_ID}
                history={history}
                {...props}
            />,
            {
                preloadedState: {
                    contributeProductionLocation: {
                        singleProductionLocation: {
                            data: location,
                            fetching: false,
                            error: null,
                        },
                    },
                },
            },
        );

    // Let the pending request promises settle.
    const flush = () => act(() => Promise.resolve());

    // The legacy fake timers do not move the clock, and the waiting
    // screen measures the time passed with it, so move both together.
    const advance = async ms => {
        await act(async () => {
            now += ms;
            jest.advanceTimersByTime(ms);
        });
        await flush();
    };

    // Let the requests settle, then wait out the moment an answer is
    // held back while the bar fills.
    const settle = async () => {
        await flush();
        await advance(RESULT_HOLD_MS);
    };

    const bar = getByRole => getByRole('progressbar');
    const barValue = getByRole =>
        Number(bar(getByRole).getAttribute('aria-valuenow'));
    const stepStates = container =>
        Array.from(container.querySelectorAll('[data-step-state]')).map(
            step => step.getAttribute('data-step-state'),
        );

    beforeEach(() => {
        jest.useFakeTimers();
        jest.clearAllMocks();
        now = 1700000000000;
        jest.spyOn(Date, 'now').mockImplementation(() => now);
        history = { push: jest.fn() };
        setReducedMotion(false);
        window.scrollTo = jest.fn();
        apiRequest.post.mockResolvedValue(answer('CHECKING'));
        apiRequest.get.mockResolvedValue(answer('CHECKING'));
    });

    afterEach(() => {
        // Unmount while the timers are still the fake ones, so the
        // component clears its own intervals rather than leaving them
        // to fire in the next test.
        cleanup();
        jest.clearAllTimers();
        jest.useRealTimers();
        Date.now.mockRestore();
    });

    test('starts the check once and tells the claimant to stay', async () => {
        const { getByText } = renderCheck();

        expect(getByText('Checking your claim')).toBeInTheDocument();
        expect(getByText(STAY)).toBeInTheDocument();

        await settle();

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        expect(apiRequest.post).toHaveBeenCalledWith(CHECK_URL);
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('the not-available screen says an email follows', async () => {
        apiRequest.get.mockResolvedValue(answer('UNAVAILABLE', [], 2));
        const { getByText } = renderCheck();
        await settle();
        await advance(POLL_INTERVAL_MS);

        expect(
            getByText('You will get an email when the claim is reviewed.'),
        ).toBeInTheDocument();
    });

    test('brings the panel into view when it appears and when it changes', async () => {
        apiRequest.post.mockResolvedValue(answer('PASSED', [], 0));
        renderCheck();

        expect(window.scrollTo).toHaveBeenCalledTimes(1);
        expect(window.scrollTo).toHaveBeenCalledWith(0, 0);

        await settle();

        expect(window.scrollTo).toHaveBeenCalledTimes(2);
    });

    test('the steps tick off as time passes, the last one only at the result', async () => {
        const { container } = renderCheck();
        await flush();

        expect(
            Array.from(container.querySelectorAll('[data-step-state]')).map(
                step => step.textContent,
            ),
        ).toEqual([
            '\u2713Claim submitted (Done)',
            'Reading your documents (In progress)',
            'Checking the company name and address (Not started)',
            'Checking your link to the company (Not started)',
        ]);

        await advance(12000);
        expect(stepStates(container)).toEqual([
            'done',
            'done',
            'now',
            'waiting',
        ]);

        await advance(18000);
        expect(stepStates(container)).toEqual(['done', 'done', 'done', 'now']);

        await advance(25000);
        expect(stepStates(container)).toEqual(['done', 'done', 'done', 'now']);

        apiRequest.get.mockResolvedValue(answer('PASSED', [], 0));
        await advance(POLL_INTERVAL_MS);
    });

    test('the bar moves fast then slow and never fills before the result', async () => {
        const { getByRole } = renderCheck();
        await flush();

        expect(bar(getByRole)).toHaveAttribute(
            'aria-label',
            'Checking your claim',
        );
        expect(bar(getByRole)).toHaveAttribute('aria-valuemin', '0');
        expect(bar(getByRole)).toHaveAttribute('aria-valuemax', '100');
        expect(barValue(getByRole)).toBe(0);

        await advance(10000);
        const early = barValue(getByRole);
        await advance(10000);
        const middle = barValue(getByRole);
        expect(early).toBeGreaterThan(30);
        expect(middle - early).toBeLessThan(early);

        await advance(25000);
        expect(barValue(getByRole)).toBe(90);

        await advance(14000);
        expect(barValue(getByRole)).toBeLessThan(100);
        expect(barValue(getByRole)).toBeLessThanOrEqual(95);
    });

    test('the bar fills and every step ticks when the result arrives, then the result shows', async () => {
        const { container, getByRole, getByText, queryByText } = renderCheck();
        await flush();
        apiRequest.get.mockResolvedValue(answer('PASSED', [], 0));

        await act(async () => {
            now += POLL_INTERVAL_MS;
            jest.advanceTimersByTime(POLL_INTERVAL_MS);
        });
        await flush();

        expect(barValue(getByRole)).toBe(100);
        expect(stepStates(container)).toEqual(['done', 'done', 'done', 'done']);
        expect(queryByText('Your claim is approved.')).toBeNull();

        await advance(RESULT_HOLD_MS);

        expect(getByText('Your claim is approved.')).toBeInTheDocument();
        expect(queryByText('Checking your claim')).toBeNull();
    });

    test('a check that is not available never shows the bar as full', async () => {
        const { getByText, queryByRole } = renderCheck();
        await flush();
        apiRequest.get.mockResolvedValue(answer('UNAVAILABLE', [], 2));

        await act(async () => {
            now += POLL_INTERVAL_MS;
            jest.advanceTimersByTime(POLL_INTERVAL_MS);
        });
        await flush();

        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        expect(queryByRole('progressbar')).toBeNull();
    });

    test('facts change every five seconds and start with the location', async () => {
        const { getByTestId } = renderCheck({
            name: 'Example Textiles',
            number_of_contributors: 4,
        });
        await flush();
        const fact = () => getByTestId('claim-live-check-fact');

        expect(fact()).toHaveAttribute('aria-live', 'off');
        expect(fact()).toHaveTextContent(
            'About this location4 organisations have shared data about Example Textiles on Open Supply Hub.',
        );

        await advance(FACT_INTERVAL_MS);
        expect(fact()).toHaveTextContent(
            'When your claim is approvedYour profile shows a Claimed badge. Buyers can see the details come from you.',
        );

        await advance(FACT_INTERVAL_MS);
        expect(fact()).toHaveTextContent(
            'When your claim is approvedYou can add your certifications, number of workers and product types.',
        );

        await advance(FACT_INTERVAL_MS);
        expect(fact()).toHaveTextContent(
            'Good to knowYou can leave this page. The result is also sent by email.',
        );

        await advance(FACT_INTERVAL_MS);
        expect(fact()).toHaveTextContent('About this location');
    });

    test('one organisation is written in the singular', async () => {
        const { getByTestId } = renderCheck({
            name: 'Example Textiles',
            contributors: [{ id: 1, name: 'Example Brand' }],
        });
        await flush();

        expect(getByTestId('claim-live-check-fact')).toHaveTextContent(
            '1 organisation has shared data about Example Textiles on Open Supply Hub.',
        );
    });

    test('the location fact is left out when its data is missing', async () => {
        const { getByTestId } = renderCheck({ name: 'Example Textiles' });
        await flush();

        expect(getByTestId('claim-live-check-fact')).toHaveTextContent(
            'Your profile shows a Claimed badge.',
        );
    });

    test('nothing is announced over and over while waiting', async () => {
        const { container, getByTestId } = renderCheck();
        await flush();
        const panel = getByTestId('claim-live-check-checking');

        expect(getByTestId('claim-live-check-fact')).toHaveAttribute(
            'aria-live',
            'off',
        );
        expect(panel.querySelector('[aria-live="polite"]')).toBeNull();
        expect(panel.querySelector('[aria-live="assertive"]')).toBeNull();
        expect(container.querySelector('[role="status"]')).toBeNull();
    });

    test('every result has a real heading and is announced once', async () => {
        apiRequest.post.mockResolvedValue(
            answer('NOT_PASSED', ['upload_document']),
        );
        const { getByRole, container } = renderCheck();
        await settle();

        expect(
            getByRole('heading', {
                name: 'Your claim did not pass the pre-check.',
            }),
        ).toBeInTheDocument();
        expect(container.querySelectorAll('[role="status"]')).toHaveLength(1);
    });

    test('a check that could not start hands back to the caller and promises nothing', async () => {
        apiRequest.post.mockResolvedValue(answer('UNAVAILABLE', [], 3));
        const onNotStarted = jest.fn();
        const { container } = renderCheck({}, { onNotStarted });
        await settle();

        expect(onNotStarted).toHaveBeenCalledTimes(1);
        expect(container).toBeEmptyDOMElement();
        await advance(POLL_INTERVAL_MS * 2);
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('a failed request to start hands back to the caller too', async () => {
        apiRequest.post.mockRejectedValue(new Error('network'));
        const onNotStarted = jest.fn();
        const { container } = renderCheck({}, { onNotStarted });
        await settle();

        expect(onNotStarted).toHaveBeenCalledTimes(1);
        expect(container).toBeEmptyDOMElement();
    });

    test('a check that started and then became unavailable stays on the page', async () => {
        apiRequest.get.mockResolvedValue(answer('UNAVAILABLE', [], 2));
        const onNotStarted = jest.fn();
        const { getByText } = renderCheck({}, { onNotStarted });
        await settle();
        await advance(POLL_INTERVAL_MS);

        expect(onNotStarted).not.toHaveBeenCalled();
        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
        expect(
            getByText('You will get an email when the claim is reviewed.'),
        ).toBeInTheDocument();
    });

    test('tells the API once when it gives up after one minute', async () => {
        const onNotStarted = jest.fn();
        const { getByText } = renderCheck({}, { onNotStarted });
        await settle();
        apiRequest.post.mockResolvedValue(answer('UNAVAILABLE', [], 2));

        await advance(CHECK_TIMEOUT_MS);
        await advance(POLL_INTERVAL_MS * 3);

        expect(apiRequest.post).toHaveBeenCalledTimes(2);
        expect(apiRequest.post).toHaveBeenLastCalledWith(CHECK_URL, {
            timed_out: true,
        });
        expect(onNotStarted).not.toHaveBeenCalled();
        expect(getByText(UNAVAILABLE)).toBeInTheDocument();
    });

    test('with reduced motion nothing is animated, facts still change and the result is not held back', async () => {
        setReducedMotion(true);
        const { getByTestId, getByText } = renderCheck();
        await flush();

        expect(getByTestId('claim-live-check-checking')).toHaveAttribute(
            'data-reduced-motion',
            'true',
        );
        await advance(FACT_INTERVAL_MS);
        expect(getByTestId('claim-live-check-fact')).toHaveTextContent(
            'You can add your certifications',
        );

        apiRequest.get.mockResolvedValue(answer('PASSED', [], 0));
        await act(async () => {
            now += POLL_INTERVAL_MS;
            jest.advanceTimersByTime(POLL_INTERVAL_MS);
        });
        await flush();

        expect(getByText('Your claim is approved.')).toBeInTheDocument();
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
        await advance(RESULT_HOLD_MS);

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
        const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

        unmount();
        // The poll, the bar and steps, and the facts each had a timer.
        expect(clearIntervalSpy.mock.calls.length).toBeGreaterThanOrEqual(3);
        clearIntervalSpy.mockRestore();
        await advance(POLL_INTERVAL_MS * 5);

        expect(apiRequest.get).toHaveBeenCalledTimes(polls);
        expect(reduxStore.getState().claimLiveCheck.claimID).toBeNull();
    });
});
