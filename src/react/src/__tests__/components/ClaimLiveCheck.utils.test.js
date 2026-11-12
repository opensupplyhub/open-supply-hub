import {
    focusFixField,
    makeFixLink,
    parseFixParams,
} from '../../components/ClaimLiveCheck/utils';
import { CLAIM_LIVE_CHECK_FIXES } from '../../components/ClaimLiveCheck/constants';
import claimLiveCheckReducer from '../../reducers/ClaimLiveCheckReducer';
import {
    completeClaimLiveCheck,
    failClaimLiveCheck,
    resetClaimLiveCheck,
    startClaimLiveCheck,
} from '../../actions/claimLiveCheck';

describe('ClaimLiveCheck preset fixes', () => {
    test('are exactly the six approved lines', () => {
        expect(
            Object.values(CLAIM_LIVE_CHECK_FIXES).map(fix => fix.text),
        ).toEqual([
            'Use a work email, not a personal email.',
            'Upload a document. Claims with a document are approved fastest.',
            'A document could not be read. Upload a clearer photo or a PDF.',
            'Add a document that shows your name and your company. For example a business card, employment letter or ID badge.',
            'Add an official document that shows the company name.',
            'Add an official document that shows the company address. For example a utility bill or business registration.',
        ]);
    });

    test('each names a field to go back to', () => {
        Object.values(CLAIM_LIVE_CHECK_FIXES).forEach(fix => {
            expect(fix.targets.length).toBeGreaterThan(0);
        });
    });
});

describe('makeFixLink', () => {
    test('carries the fix and the request to check again', () => {
        expect(makeFixLink(12, 'work_email', true)).toBe(
            '/claimed/pending/12?fix=work_email&check=1',
        );
    });

    test('leaves out the check when none is left', () => {
        expect(makeFixLink(12, 'upload_document', false)).toBe(
            '/claimed/pending/12?fix=upload_document',
        );
    });

    test('leaves out a fix it does not know', () => {
        expect(makeFixLink(12, 'made_up', false)).toBe('/claimed/pending/12');
        expect(makeFixLink(12, undefined, true)).toBe(
            '/claimed/pending/12?check=1',
        );
    });
});

describe('parseFixParams', () => {
    test('reads a known fix and the check flag', () => {
        expect(parseFixParams('?fix=company_name_document&check=1')).toEqual({
            fix: 'company_name_document',
            checkAgain: true,
        });
    });

    test('ignores anything it does not know', () => {
        expect(
            parseFixParams('?fix=%3Cscript%3E&check=yes&other=1'),
        ).toEqual({ fix: null, checkAgain: false });
        expect(parseFixParams('?fix=toString')).toEqual({
            fix: null,
            checkAgain: false,
        });
    });

    test('copes with no query string', () => {
        expect(parseFixParams('')).toEqual({ fix: null, checkAgain: false });
        expect(parseFixParams(undefined)).toEqual({
            fix: null,
            checkAgain: false,
        });
    });
});

describe('focusFixField', () => {
    const render = html => {
        const root = document.createElement('div');
        root.innerHTML = html;
        document.body.appendChild(root);
        root.querySelectorAll('*').forEach(element => {
            // JSDOM does not implement scrollIntoView.
            // eslint-disable-next-line no-param-reassign
            element.scrollIntoView = jest.fn();
        });
        return root;
    };

    afterEach(() => {
        document.body.innerHTML = '';
    });

    test('goes to the upload box when it is on the page', () => {
        const root = render(
            '<select id="locationAddressVerificationMethod"></select>' +
                '<label for="company-address-verification-documents">Upload</label>',
        );
        const label = root.querySelector('label');

        expect(focusFixField('company_address_document', root)).toBe(true);

        expect(label.scrollIntoView).toHaveBeenCalledWith({ block: 'center' });
        expect(document.activeElement).toBe(label);
    });

    test('falls back to the proof question when there is no upload box', () => {
        const root = render(
            '<select id="locationAddressVerificationMethod"></select>',
        );

        expect(focusFixField('upload_document', root)).toBe(true);

        expect(document.activeElement).toBe(root.querySelector('select'));
    });

    test('goes to the employment proof for the name and company fix', () => {
        const root = render(
            '<select id="claimantEmploymentVerificationMethod"></select>' +
                '<select id="locationAddressVerificationMethod"></select>',
        );

        focusFixField('name_and_company_document', root);

        expect(document.activeElement.id).toBe(
            'claimantEmploymentVerificationMethod',
        );
    });

    test('scrolls to the read-only email for the work email fix', () => {
        const root = render('<input id="claimant-email" disabled />');
        const input = root.querySelector('input');

        expect(focusFixField('work_email', root)).toBe(true);
        expect(input.scrollIntoView).toHaveBeenCalled();
    });

    test('does nothing for an unknown fix or a missing field', () => {
        const root = render('<input id="something-else" />');

        expect(focusFixField('made_up', root)).toBe(false);
        expect(focusFixField('work_email', root)).toBe(false);
    });
});

describe('claimLiveCheck reducer', () => {
    const started = claimLiveCheckReducer(
        undefined,
        startClaimLiveCheck({ claimID: 5 }),
    );

    test('keeps the answer for the claim being checked', () => {
        const state = claimLiveCheckReducer(
            started,
            completeClaimLiveCheck({
                claimID: 5,
                data: {
                    status: 'NOT_PASSED',
                    fixes: ['work_email'],
                    checks_left: 1,
                    ai_decision_reason: 'not for claimants',
                },
            }),
        );

        expect(state).toEqual({
            claimID: 5,
            status: 'NOT_PASSED',
            fixes: ['work_email'],
            checksLeft: 1,
        });
    });

    test('drops an answer or a failure for another claim', () => {
        const stale = { claimID: 4, data: { status: 'PASSED', fixes: [] } };

        expect(
            claimLiveCheckReducer(started, completeClaimLiveCheck(stale)),
        ).toBe(started);
        expect(
            claimLiveCheckReducer(started, failClaimLiveCheck({ claimID: 4 })),
        ).toBe(started);
    });

    test('drops an answer that arrives after a reset', () => {
        const reset = claimLiveCheckReducer(started, resetClaimLiveCheck());

        expect(
            claimLiveCheckReducer(
                reset,
                completeClaimLiveCheck({
                    claimID: 5,
                    data: { status: 'PASSED', fixes: [] },
                }),
            ),
        ).toBe(reset);
    });

    test('a failure reads as not available', () => {
        const state = claimLiveCheckReducer(
            started,
            failClaimLiveCheck({ claimID: 5 }),
        );

        expect(state.status).toBe('UNAVAILABLE');
        expect(state.fixes).toEqual([]);
    });
});
