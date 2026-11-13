import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { fireEvent, waitFor } from '@testing-library/react';

import ProductionLocationDetailsContent from '../../components/ProductionLocation/ProductionLocationDetailsContent/ProductionLocationDetailsContent';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import apiRequest from '../../util/apiRequest';
import { getStrengthenSteps } from '../../components/ProductionLocation/ProfileCompleteness/utils';

jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
}));
jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsMap/ProductionLocationDetailsMap',
    () => () => <div data-testid="details-map" />,
);
jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields',
    () => () => <div data-testid="general-fields">General Information</div>,
);
jest.mock(
    '../../components/ProductionLocation/ClaimSection/ClaimDataContainer/ClaimDataContainer',
    () => () => null,
);
jest.mock(
    '../../components/ProductionLocation/PartnerSection/PartnerDataContainer/PartnerDataContainer',
    () => () => null,
);

const OS_ID = 'IN20190866W0EJK';

const componentValues = {
    claimed_status: 1,
    recency_score: 0.84,
    contribution_count_score: 0.68,
    contribution_mix_score: 0.67,
    completeness_score: 0.667,
    claimed_only_score: 0.15,
    assessments_audits_score: 1,
    certifications_score: 0,
};

const makeComponents = values =>
    Object.keys(values).map(key => ({
        key,
        label: `label ${key}`,
        value: values[key],
    }));

const makeResponse = (overrides = {}) => ({
    os_id: OS_ID,
    score: {
        value: 0.627,
        level: 2,
        level_name: 'Enhanced',
        max_level: 3,
        components: makeComponents(componentValues),
        scorer_version: 'v111126',
        run_date: '2026-11-11',
    },
    classifier: {
        tier: 'high',
        level: 3,
        level_name: 'Extensive',
        agreement_tier: 'best',
        field_tier: 'high',
        model: 'model-1.0',
        run_date: '2026-11-12',
    },
    ...overrides,
});

const signedInState = {
    auth: { user: { user: { isAnon: false, id: 1 } } },
};

const renderContent = ({ preloadedState = signedInState, props = {} } = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <ProductionLocationDetailsContent
                data={{ properties: { os_id: OS_ID, claim_info: null } }}
                {...props}
            />
        </MemoryRouter>,
        { preloadedState },
    );

describe('ProductionLocation profile completeness preview', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
    });

    test('makes no request and renders nothing for a signed-out visitor', () => {
        const { queryByTestId } = renderContent({ preloadedState: {} });

        expect(apiRequest.get).not.toHaveBeenCalled();
        expect(
            queryByTestId('profile-completeness-indicator'),
        ).not.toBeInTheDocument();
        expect(
            queryByTestId('profile-completeness-calculation'),
        ).not.toBeInTheDocument();
    });

    test('makes no request on an embedded profile', () => {
        renderContent({ props: { embed: true } });

        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('renders nothing when the endpoint answers 404', async () => {
        apiRequest.get.mockRejectedValue({ response: { status: 404 } });

        const { queryByTestId } = renderContent();

        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                `/api/profile-completeness/${OS_ID}/`,
            ),
        );
        expect(
            queryByTestId('profile-completeness-indicator'),
        ).not.toBeInTheDocument();
    });

    test('shows one filled bar per level under the claim status', async () => {
        apiRequest.get.mockResolvedValue({ data: makeResponse() });

        const { findByTestId, getAllByTestId, getByTestId } = renderContent();

        const indicator = await findByTestId('profile-completeness-indicator');
        expect(indicator).toHaveTextContent('Profile completeness');
        expect(indicator).toHaveAttribute(
            'aria-label',
            expect.stringContaining('Enhanced (level 2 of 3)'),
        );
        expect(getByTestId('profile-completeness-level-name')).toHaveTextContent(
            'Enhanced',
        );
        expect(getAllByTestId('profile-completeness-bar-filled')).toHaveLength(
            2,
        );
        expect(getAllByTestId('profile-completeness-bar-empty')).toHaveLength(
            1,
        );
        expect(getByTestId('claim-banner').nextElementSibling).toBe(indicator);
    });

    test('opens the breakdown from the indicator', async () => {
        apiRequest.get.mockResolvedValue({ data: makeResponse() });

        const { findByTestId, getByTestId, getByText } = renderContent();

        const section = getByTestId.bind(
            null,
            'profile-completeness-calculation',
        );
        fireEvent.click(await findByTestId('profile-completeness-indicator'));

        expect(
            section().querySelector('[aria-expanded="true"]'),
        ).not.toBeNull();
        expect(getByTestId('profile-completeness-score')).toHaveTextContent(
            '0.627',
        );
        expect(getByText('label recency_score')).toBeInTheDocument();
        expect(section()).toHaveTextContent('Admin preview');
        expect(section()).toHaveTextContent('Scorer v111126');
    });

    test('shows the model classification next to the score', async () => {
        apiRequest.get.mockResolvedValue({ data: makeResponse() });

        const { findByTestId, getByTestId } = renderContent();

        const classifier = await findByTestId(
            'profile-completeness-classifier',
        );
        expect(classifier).toHaveTextContent('Model classification');
        expect(classifier).toHaveTextContent('High');
        expect(classifier).toHaveTextContent('Best');
        expect(classifier).toHaveTextContent('model-1.0');
        expect(
            getByTestId('profile-completeness-comparison'),
        ).toHaveTextContent(
            'Different: the score gives Enhanced (level 2 of 3), the classification corresponds to Extensive (level 3 of 3)',
        );
    });

    test('says when the classification and the score agree', async () => {
        apiRequest.get.mockResolvedValue({
            data: makeResponse({
                classifier: {
                    tier: 'medium',
                    level: 2,
                    level_name: 'Enhanced',
                    agreement_tier: 'medium',
                    field_tier: 'high',
                    model: 'model-1.0',
                    run_date: '2026-11-12',
                },
            }),
        });

        const { findByTestId } = renderContent();

        expect(
            await findByTestId('profile-completeness-comparison'),
        ).toHaveTextContent('Same level: Enhanced (level 2 of 3)');
    });

    test('shows the classification alone when there is no score', async () => {
        apiRequest.get.mockResolvedValue({
            data: makeResponse({ score: null }),
        });

        const { findByTestId, queryByTestId } = renderContent();

        expect(
            await findByTestId('profile-completeness-classifier'),
        ).toBeInTheDocument();
        expect(
            queryByTestId('profile-completeness-indicator'),
        ).not.toBeInTheDocument();
        expect(
            queryByTestId('profile-completeness-strengthen'),
        ).not.toBeInTheDocument();
        expect(
            queryByTestId('profile-completeness-comparison'),
        ).not.toBeInTheDocument();
    });

    test('lists next steps for what the profile is missing', async () => {
        apiRequest.get.mockResolvedValue({ data: makeResponse() });

        const { findByTestId } = renderContent();

        const strengthen = await findByTestId(
            'profile-completeness-strengthen',
        );
        expect(strengthen).toHaveTextContent('3 suggested next steps');
        expect(strengthen).toHaveTextContent('Add core profile fields');
        expect(strengthen).toHaveTextContent(
            'Add more detail to the claimed profile',
        );
        expect(strengthen).toHaveTextContent(
            'Add certification records, if any apply',
        );
        expect(strengthen).not.toHaveTextContent('Claim this profile');
    });
});

describe('getStrengthenSteps', () => {
    test('leads with claiming for an unclaimed, thin profile', () => {
        const steps = getStrengthenSteps(
            makeComponents({
                claimed_status: 0,
                recency_score: 0.5,
                contribution_count_score: 0.3,
                contribution_mix_score: 0.3,
                completeness_score: 0.5,
                claimed_only_score: 0,
                assessments_audits_score: 0,
                certifications_score: 0,
            }),
        );

        expect(steps.map(step => step.key)).toEqual([
            'claim',
            'fields',
            'contributors',
        ]);
    });

    test('returns nothing when every component is full', () => {
        const steps = getStrengthenSteps(
            makeComponents({
                claimed_status: 1,
                recency_score: 1,
                contribution_count_score: 1,
                contribution_mix_score: 1,
                completeness_score: 1,
                claimed_only_score: 1,
                assessments_audits_score: 1,
                certifications_score: 1,
            }),
        );

        expect(steps).toEqual([]);
    });
});
