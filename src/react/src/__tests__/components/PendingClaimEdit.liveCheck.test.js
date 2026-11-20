import React from 'react';
import { act, fireEvent, waitFor } from '@testing-library/react';
import { Route, Router } from 'react-router-dom';

import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PendingClaimEdit from '../../components/PendingClaimEdit/PendingClaimEdit';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
    post: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
}));

// The reused claim-form steps are heavy and have their own tests
// (the marks on their fields are in ClaimLiveCheckFieldFixes.test.js).
// The stand-ins carry the fields the live check fixes point at and
// show which fixes the page handed them.
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep',
    () => ({ liveCheckFixes }) => (
        <div
            data-testid="contact-step"
            data-fixes={JSON.stringify(liveCheckFixes)}
        >
            <div id="claimant-email-helper-text" aria-label="Your Email" />
            <select
                id="claimantEmploymentVerificationMethod"
                aria-label="Employment Verification"
            />
        </div>
    ),
);
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep',
    () => ({ liveCheckFixes }) => (
        <div
            data-testid="business-step"
            data-fixes={JSON.stringify(liveCheckFixes)}
        >
            <select
                id="locationAddressVerificationMethod"
                aria-label="Company Address Verification"
            />
        </div>
    ),
);
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/ProfileStep/ProfileStep',
    () => () => <div data-testid="profile-step" />,
);
jest.mock('../../components/PendingClaimEdit/PendingClaimAttachments', () => () => (
    <div data-testid="attachments" />
));
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/validationSchemas',
    () => {
        // eslint-disable-next-line global-require
        const Yup = require('yup');
        return {
            contactStepSchema: Yup.object(),
            businessStepSchema: Yup.object(),
            profileStepSchema: Yup.object(),
        };
    },
);

const CLAIM_ID = '12';
const PENDING_URL = `/api/facility-claims/${CLAIM_ID}/pending/`;
const LIVE_CHECK_URL = `/api/facility-claims/${CLAIM_ID}/live-check/`;
const SAVE_AND_CHECK = 'Save and check again';
const CHECKING = 'We are checking your claim. Stay for your result.';
const THANK_YOU = 'Thank you for editing your claim request!';

const pendingClaim = {
    id: 12,
    os_id: 'US2020123ABC456',
    facility_name: 'Example Textiles',
    created_at: '2026-01-05T10:00:00Z',
    your_name: 'Example Claimant',
    your_title: 'Owner',
    attachments: [],
};

const stateWith = flags => ({
    featureFlags: { fetching: false, flags },
    filterOptions: {
        countries: {
            data: [{ value: 'US', label: 'United States' }],
            fetching: false,
            error: null,
        },
        facilityProcessingType: {
            data: [{ value: 'assembly', label: 'Assembly' }],
            fetching: false,
            error: null,
        },
    },
});

const renderEditPage = (search, flags = { claim_live_check: true }) => {
    history.push(`/claimed/pending/${CLAIM_ID}${search}`);
    return renderWithProviders(
        <Router history={history}>
            <Route
                path="/claimed/pending/:claimID"
                component={PendingClaimEdit}
            />
        </Router>,
        { preloadedState: stateWith(flags) },
    );
};

describe('PendingClaimEdit after "Go back and fix it"', () => {
    // The test environment is node with a JSDOM window (setupTests.js).
    // Formik's handleSubmit looks for this global.
    beforeAll(() => {
        window.scrollTo = jest.fn();
        global.HTMLButtonElement = window.HTMLButtonElement;
    });
    afterAll(() => {
        delete global.HTMLButtonElement;
    });

    beforeEach(() => {
        jest.clearAllMocks();
        // The claim has no live check with fixes that are still current.
        apiRequest.get.mockImplementation(url => {
            if (url === PENDING_URL) {
                return Promise.resolve({ data: pendingClaim });
            }
            if (url === LIVE_CHECK_URL) {
                return Promise.resolve({
                    data: { status: 'UNAVAILABLE', fixes: [], checks_left: 3 },
                });
            }
            return Promise.reject(new Error('not mocked'));
        });
        apiRequest.patch.mockResolvedValue({ data: pendingClaim });
        apiRequest.post.mockResolvedValue({
            data: { status: 'CHECKING', fixes: [], checks_left: 1 },
        });
    });

    test('opens at the field to fix and offers to check again', async () => {
        const { findByText, getByLabelText } = renderEditPage(
            '?fix=upload_document&check=1',
        );

        expect(await findByText(SAVE_AND_CHECK)).toBeInTheDocument();
        await waitFor(() =>
            expect(document.activeElement).toBe(
                getByLabelText('Company Address Verification'),
            ),
        );
    });

    test('saving checks the claim again in place of the thank-you dialog', async () => {
        const { findByText, queryByText } = renderEditPage(
            '?fix=upload_document&check=1',
        );

        fireEvent.click(await findByText(SAVE_AND_CHECK));

        expect(await findByText(CHECKING)).toBeInTheDocument();
        expect(apiRequest.patch).toHaveBeenCalledWith(
            PENDING_URL,
            expect.anything(),
        );
        expect(apiRequest.post).toHaveBeenCalledWith(LIVE_CHECK_URL);
        expect(queryByText(THANK_YOU)).toBeNull();
    });

    test('a check that cannot start ends with the usual thank-you dialog', async () => {
        apiRequest.post.mockResolvedValue({
            data: { status: 'UNAVAILABLE', fixes: [], checks_left: 2 },
        });
        const { findByText, queryByText } = renderEditPage(
            '?fix=upload_document&check=1',
        );

        fireEvent.click(await findByText(SAVE_AND_CHECK));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(queryByText(CHECKING)).toBeNull();
        expect(queryByText(/email/i)).toBeNull();
    });

    test('opened the usual way it saves as it always has', async () => {
        const { findByText, queryByText } = renderEditPage('');

        fireEvent.click(await findByText('Save changes'));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(queryByText(SAVE_AND_CHECK)).toBeNull();
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test('with the switch off the page is as it always was', async () => {
        const {
            findByText,
            getByLabelText,
            queryByRole,
            queryByText,
        } = renderEditPage('?fix=upload_document&check=1', {
            claim_live_check: false,
        });

        // Moving within the page does not read the claim again.
        await findByText('Save changes');
        act(() => history.push(`/claimed/pending/${CLAIM_ID}?check=1`));
        expect(
            apiRequest.get.mock.calls.filter(([url]) => url === PENDING_URL),
        ).toHaveLength(1);
        expect(queryByRole('status')).toBeNull();

        fireEvent.click(await findByText('Save changes'));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(queryByText(SAVE_AND_CHECK)).toBeNull();
        expect(document.activeElement).not.toBe(
            getByLabelText('Company Address Verification'),
        );
        expect(apiRequest.post).not.toHaveBeenCalled();
        expect(apiRequest.get).not.toHaveBeenCalledWith(LIVE_CHECK_URL);
    });
});

describe('PendingClaimEdit marks every field the latest check flagged', () => {
    const SEVERAL = {
        status: 'NOT_PASSED',
        fixes: [
            'work_email',
            'upload_document',
            'name_and_company_document',
            'company_address_document',
        ],
        checks_left: 2,
    };
    const BY_FIELD = {
        email: ['work_email'],
        address: ['upload_document', 'company_address_document'],
        employment: ['name_and_company_document'],
    };

    let liveCheck;

    const fixesOf = element => JSON.parse(element.getAttribute('data-fixes'));

    beforeAll(() => {
        window.scrollTo = jest.fn();
        global.HTMLButtonElement = window.HTMLButtonElement;
    });
    afterAll(() => {
        delete global.HTMLButtonElement;
    });

    beforeEach(() => {
        jest.clearAllMocks();
        liveCheck = SEVERAL;
        apiRequest.get.mockImplementation(url => {
            if (url === PENDING_URL) {
                return Promise.resolve({ data: pendingClaim });
            }
            if (url === LIVE_CHECK_URL) {
                return Promise.resolve({ data: liveCheck });
            }
            return Promise.reject(new Error('not mocked'));
        });
        apiRequest.patch.mockResolvedValue({ data: pendingClaim });
        apiRequest.post.mockResolvedValue({
            data: { status: 'CHECKING', fixes: [], checks_left: 1 },
        });
    });

    // The same marks whichever way the claimant arrives: from the
    // result screen or the email link (both carry the query string),
    // or from My Claims (no query string).
    test.each([
        ['from the result screen or the email link', '?fix=work_email&check=1'],
        ['from My Claims', ''],
    ])('%s', async (_, search) => {
        const { findByRole, getByTestId, getByText } = renderEditPage(search);

        const banner = await findByRole('status');
        expect(banner).toHaveTextContent('4 things to fix');
        expect(fixesOf(getByTestId('contact-step'))).toEqual(BY_FIELD);
        expect(fixesOf(getByTestId('business-step'))).toEqual(BY_FIELD);
        // One link per field, however many fixes are about it.
        expect(
            Array.from(banner.querySelectorAll('button')).map(
                button => button.textContent,
            ),
        ).toEqual([
            'Your email',
            'Company address verification',
            'Employment verification',
        ]);
        expect(getByText(SAVE_AND_CHECK)).toBeInTheDocument();
    });

    test('one fix is counted in the singular', async () => {
        liveCheck = {
            status: 'NOT_PASSED',
            fixes: ['upload_document'],
            checks_left: 2,
        };
        const { findByRole } = renderEditPage('');

        expect(await findByRole('status')).toHaveTextContent('1 thing to fix');
    });

    test('each link takes the keyboard focus to its field', async () => {
        const { findByText, getByText, getByLabelText } = renderEditPage('');

        fireEvent.click(await findByText('Company address verification'));
        expect(document.activeElement).toBe(
            getByLabelText('Company Address Verification'),
        );

        fireEvent.click(getByText('Employment verification'));
        expect(document.activeElement).toBe(
            getByLabelText('Employment Verification'),
        );

        fireEvent.click(getByText('Your email'));
        expect(document.activeElement).toBe(getByLabelText('Your Email'));
    });

    test.each([
        ['a check that passed', { status: 'PASSED', fixes: ['upload_document'] }],
        ['a check still running', { status: 'CHECKING', fixes: [] }],
        ['a claim edited since', { status: 'UNAVAILABLE', fixes: [] }],
        ['an unknown fix', { status: 'NOT_PASSED', fixes: ['Raw model text'] }],
    ])('nothing is marked for %s', async (_, answer) => {
        liveCheck = { ...answer, checks_left: 2 };
        const { findByText, queryByRole, queryByText } = renderEditPage('');

        expect(await findByText('Save changes')).toBeInTheDocument();
        expect(queryByRole('status')).toBeNull();
        expect(queryByText(/Raw model text/)).toBeNull();
    });

    test('a failed read leaves the page as it always was', async () => {
        apiRequest.get.mockImplementation(url =>
            url === PENDING_URL
                ? Promise.resolve({ data: pendingClaim })
                : Promise.reject(new Error('network')),
        );
        const { findByText, queryByRole } = renderEditPage('');

        expect(await findByText('Save changes')).toBeInTheDocument();
        expect(queryByRole('status')).toBeNull();
    });

    test('with no checks left the fields are marked but saving does not check again', async () => {
        liveCheck = { ...SEVERAL, checks_left: 0 };
        const { findByRole, getByText, findByText } = renderEditPage('');

        expect(await findByRole('status')).toHaveTextContent('4 things to fix');
        fireEvent.click(getByText('Save changes'));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test('going back from a second result opens the form again with the new marks', async () => {
        const { findByText, findByRole, getByTestId } = renderEditPage('');
        const second = {
            status: 'NOT_PASSED',
            fixes: ['company_name_document'],
            checks_left: 1,
        };
        apiRequest.post.mockResolvedValue({ data: second });

        fireEvent.click(await findByText(SAVE_AND_CHECK));
        liveCheck = second;
        fireEvent.click(await findByText('Go back and fix it'));

        const banner = await findByRole('status');
        expect(banner).toHaveTextContent('1 thing to fix');
        expect(fixesOf(getByTestId('business-step'))).toEqual({
            address: ['company_name_document'],
        });
        expect(await findByText(SAVE_AND_CHECK)).toBeInTheDocument();
    });
});
