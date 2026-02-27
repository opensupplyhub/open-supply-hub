import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, within, fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { setupStore } from '../../configureStore';
import ContributeFields from '../../components/ProductionLocation/Sidebar/ContributeFields/ContributeFields';
import { USER_DEFAULT_STATE } from '../../util/constants';
import { completeFetchSingleFacility } from '../../actions/facilities';

const TEST_OS_ID = 'US2026055ETKBY0';

const minimalFacilityFeature = {
    id: TEST_OS_ID,
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [-73.83, 40.76],
    },
    properties: {
        name: 'Test Facility Name',
        address: '123 Test St',
        country_code: 'US',
        country_name: 'United States',
        is_closed: false,
    },
};

const getDefaultPreloadedState = (overrides = {}) => {
    const defaultState = {
        facilities: {
            singleFacility: {
                data: minimalFacilityFeature,
                fetching: false,
                error: null,
            },
        },
        auth: {
            user: {
                user: { ...USER_DEFAULT_STATE },
            },
        },
        dashboardActivityReports: {
            activityReports: {
                data: [],
                fetching: false,
                error: null,
                message: null,
            },
        },
    };
    return {
        ...defaultState,
        ...overrides,
        facilities: {
            ...defaultState.facilities,
            ...(overrides.facilities || {}),
            singleFacility: {
                ...defaultState.facilities.singleFacility,
                ...(overrides.facilities?.singleFacility || {}),
            },
        },
        auth: {
            ...defaultState.auth,
            ...(overrides.auth || {}),
            user: {
                ...defaultState.auth.user,
                ...(overrides.auth?.user || {}),
                user: {
                    ...defaultState.auth.user.user,
                    ...(overrides.auth?.user?.user || {}),
                },
            },
        },
    };
}

const renderContributeFields = (preloadedStateOverrides = {}, props = {}) => {
    const preloadedState = getDefaultPreloadedState(preloadedStateOverrides);

    return renderWithProviders(
        <MemoryRouter>
            <ContributeFields osId={props.osId ?? TEST_OS_ID} />
        </MemoryRouter>,
        { preloadedState },
    );
}

describe('ContributeFields and ReportFacilityStatusDialog', () => {
    describe('ContributeFields section', () => {
        test('renders contribute section with test id', () => {
            renderContributeFields();

            expect(screen.getByTestId('contribute-fields')).toBeInTheDocument();
        });

        test('renders suggest correction link with correct path', () => {
            renderContributeFields();

            const link = screen.getByTestId('contribute-suggest-correction');
            expect(link).toBeInTheDocument();
            expect(link).toHaveAttribute(
                'href',
                expect.stringContaining(`/contribute/single-location/${TEST_OS_ID}/info/`),
            );
        });

        test('renders report duplicate mailto link', () => {
            renderContributeFields();

            const link = screen.getByTestId('contribute-report-duplicate');
            expect(link).toBeInTheDocument();
            expect(link).toHaveAttribute('href', expect.stringMatching(/^mailto:/));
        });

        test('renders report status action that opens dialog', () => {
            renderContributeFields();

            expect(screen.getByTestId('contribute-report-status')).toBeInTheDocument();
        });

        test('renders report status action when facility is closed', () => {
            const closedFacility = {
                ...minimalFacilityFeature,
                properties: {
                    ...minimalFacilityFeature.properties,
                    is_closed: true,
                },
            };
            renderContributeFields({
                facilities: {
                    singleFacility: {
                        data: closedFacility,
                        fetching: false,
                        error: null,
                    },
                },
            });

            expect(screen.getByTestId('contribute-report-status')).toBeInTheDocument();
        });
    });

    describe('ReportFacilityStatusDialog integration', () => {
        test('opening report status shows dialog with facility data', () => {
            renderContributeFields();

            expect(screen.queryByTestId('report-facility-status-dialog')).not.toBeInTheDocument();

            fireEvent.click(screen.getByTestId('contribute-report-status'));

            const dialog = screen.getByTestId('report-facility-status-dialog');
            expect(dialog).toBeInTheDocument();
            expect(
                within(dialog).getByTestId('report-facility-status-dialog-facility-name'),
            ).toHaveTextContent(minimalFacilityFeature.properties.name);
        });

        test('when single facility data is null dialog does not render content when opened', () => {
            renderContributeFields({
                facilities: {
                    singleFacility: {
                        data: null,
                        fetching: false,
                        error: null,
                    },
                },
            });

            fireEvent.click(screen.getByTestId('contribute-report-status'));

            expect(screen.queryByTestId('report-facility-status-dialog')).not.toBeInTheDocument();
        });

        test('anonymous user sees login prompt in dialog', () => {
            renderContributeFields();

            fireEvent.click(screen.getByTestId('contribute-report-status'));

            expect(
                screen.getByTestId('report-facility-status-dialog-login'),
            ).toBeInTheDocument();
        });

        test('logged-in user sees reason field and report action', () => {
            renderContributeFields({
                auth: {
                    user: {
                        user: {
                            ...USER_DEFAULT_STATE,
                            isAnon: false,
                        },
                    },
                },
            });

            fireEvent.click(screen.getByTestId('contribute-report-status'));

            expect(screen.getByTestId('report-facility-status-reason')).toBeInTheDocument();
            expect(
                screen.getByTestId('report-facility-status-dialog-cancel'),
            ).toBeInTheDocument();
            expect(
                screen.getByTestId('report-facility-status-dialog-report'),
            ).toBeInTheDocument();
        });

        test('cancel closes dialog', () => {
            renderContributeFields({
                auth: {
                    user: {
                        user: {
                            ...USER_DEFAULT_STATE,
                            isAnon: false,
                        },
                    },
                },
            });

            fireEvent.click(screen.getByTestId('contribute-report-status'));
            expect(screen.getByTestId('report-facility-status-dialog')).toBeInTheDocument();

            fireEvent.click(screen.getByTestId('report-facility-status-dialog-cancel'));

            const dialogAfterClose = screen.getByTestId('report-facility-status-dialog');
            expect(dialogAfterClose).not.toBeVisible();
        });

        test('report with empty reason keeps dialog open', () => {
            renderContributeFields({
                auth: {
                    user: {
                        user: {
                            ...USER_DEFAULT_STATE,
                            isAnon: false,
                        },
                    },
                },
            });

            fireEvent.click(screen.getByTestId('contribute-report-status'));
            fireEvent.click(screen.getByTestId('report-facility-status-dialog-report'));

            expect(screen.getByTestId('report-facility-status-dialog')).toBeInTheDocument();
        });
    });

    describe('Redux state via actions', () => {
        test('prefilled facility via completeFetchSingleFacility is used by dialog', () => {
            const store = setupStore({});
            store.dispatch(completeFetchSingleFacility(minimalFacilityFeature));

            const { getByTestId } = renderWithProviders(
                <MemoryRouter>
                    <ContributeFields osId={TEST_OS_ID} />
                </MemoryRouter>,
                { reduxStore: store },
            );

            fireEvent.click(getByTestId('contribute-report-status'));

            expect(getByTestId('report-facility-status-dialog')).toBeInTheDocument();
            expect(
                getByTestId('report-facility-status-dialog-facility-name'),
            ).toHaveTextContent(minimalFacilityFeature.properties.name);
        });
    });
});
