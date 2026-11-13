import React from 'react';
import { fireEvent, waitFor } from '@testing-library/react';
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

// The reused claim-form steps are heavy and have their own tests. The
// Business step stand-in carries the field a live check fix points at.
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep',
    () => () => <div data-testid="contact-step" />,
);
jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep',
    () => () => (
        <div data-testid="business-step">
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
        apiRequest.get.mockImplementation(url =>
            url === PENDING_URL
                ? Promise.resolve({ data: pendingClaim })
                : Promise.reject(new Error('not mocked')),
        );
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

        expect(await findByText('Checking your claim')).toBeInTheDocument();
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
        expect(queryByText('Checking your claim')).toBeNull();
        expect(queryByText(/email/i)).toBeNull();
    });

    test('opened the usual way it saves as it always has', async () => {
        const { findByText, queryByText } = renderEditPage('');

        fireEvent.click(await findByText('Save changes'));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(queryByText(SAVE_AND_CHECK)).toBeNull();
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test('with the switch off the query string changes nothing', async () => {
        const { findByText, getByLabelText, queryByText } = renderEditPage(
            '?fix=upload_document&check=1',
            { claim_live_check: false },
        );

        fireEvent.click(await findByText('Save changes'));

        expect(await findByText(THANK_YOU)).toBeInTheDocument();
        expect(queryByText(SAVE_AND_CHECK)).toBeNull();
        expect(document.activeElement).not.toBe(
            getByLabelText('Company Address Verification'),
        );
        expect(apiRequest.post).not.toHaveBeenCalled();
    });
});
