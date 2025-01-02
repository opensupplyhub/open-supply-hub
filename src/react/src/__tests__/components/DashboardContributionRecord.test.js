import React from 'react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import { waitFor } from '@testing-library/react';
import DashboardContributionRecord from '../../components/Dashboard/DashboardContributionRecord';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
  fetchSingleModerationEvent,
  fetchPotentialMatches,
  updateSingleModerationEvent,
  createProductionLocationFromModerationEvent,
  confirmPotentialMatchFromModerationEvent,
  completeFetchPotentialMatches,
} from '../../actions/dashboardContributionRecord';

jest.resetModules();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: jest.fn(),
}));

jest.mock('../../actions/dashboardContributionRecord', () => {
  const actualActions = jest.requireActual('../../actions/dashboardContributionRecord');
  return {
    ...actualActions,
    fetchSingleModerationEvent: jest.fn(),
    updateSingleModerationEvent: jest.fn(),
    createProductionLocationFromModerationEvent: jest.fn(),
    confirmPotentialMatchFromModerationEvent: jest.fn(),
    fetchPotentialMatches: jest.fn(),
  };
});

const mockHistoryPush = jest.fn();

describe('DashboardContributionRecord component', () => {
  const routeProps = {
    match: {
        params: {
            moderationID: '9865b3a3-6eb0-4475-a75a-60002ade2eb2',
        },
    },
    history: {
      push: mockHistoryPush,
    },
  };

  const data = {
    moderation_id: '9865b3a3-6eb0-4475-a75a-60002ade2eb2',
    created_at: '2024-11-17T11:33:20.287Z',
    updated_at: '2024-12-18T21:30:20.187Z',
    os_id: 'CN2021250D1DTU7',
    cleaned_data: {
        name: 'Eco Friendly Plastics Test',
        address: '764 Main St, Manhattan, NY - USA',
        country: {
            name: 'Germany',
            alpha_2: 'DE',
            alpha_3: 'DEU',
            numeric: '286',
        },
    },
    contributor_id: 0,
    contributor_name: 'Green Solutions Corp Test',
    request_type: 'CREATE',
    source: 'API',
    moderation_status: 'PENDING',
    moderation_decision_date: null,
    claim_id: 1,
  };

  const preloadedState = {
    dashboardContributionRecord: {
      singleModerationEvent: {
        fetching: false,
        error: null,
        data,
      },
      potentialMatches: {
        matches: [],
        fetching: false,
        error: null,
      },
    },
  };

  const renderComponent = (stateOverrides = {}) => (
    renderWithProviders(
      <Router>
        <DashboardContributionRecord {...routeProps} />
      </Router>,
      {
        preloadedState: {
          ...preloadedState,
          dashboardContributionRecord: {
            ...preloadedState.dashboardContributionRecord,
            singleModerationEvent: {
              ...preloadedState.dashboardContributionRecord.singleModerationEvent,
              ...stateOverrides.dashboardContributionRecord?.singleModerationEvent,
            },
            potentialMatches: {
              ...preloadedState.dashboardContributionRecord.potentialMatches,
              ...stateOverrides.dashboardContributionRecord?.potentialMatches,
            },
          },
        },
      }
    )
  )

  beforeEach(() => {
    jest.clearAllMocks();
    useHistory.mockReturnValue({
      push: mockHistoryPush,
    });
    fetchSingleModerationEvent.mockReturnValue(() => Promise.resolve());
    updateSingleModerationEvent.mockReturnValue(() => Promise.resolve());
    fetchPotentialMatches.mockReturnValue(() => Promise.resolve());
    createProductionLocationFromModerationEvent.mockReturnValue(() =>
      Promise.resolve()
    );
    confirmPotentialMatchFromModerationEvent.mockReturnValue(() =>
      Promise.resolve()
    );
  });

  test('should render the CreateButton', () => {
    const { getByText } = renderComponent();

    expect(getByText('Create New Location')).toBeInTheDocument();
  });

  test('should render the RejectButton', () => {
    const { getByText } = renderComponent();

    expect(getByText('Reject Contribution')).toBeInTheDocument();
  });

  test('should render the ClaimButton', () => {
    const { getByText } = renderComponent();

    expect(getByText('Go to Claim')).toBeInTheDocument();
  });

  test('should disable button when eventFetching is true', () => {
    const { getByRole } = renderComponent(
      {
        dashboardContributionRecord: {
          singleModerationEvent: {
            fetching: true
          }
        }
      }
    );
    const createButton = getByRole('button', { name: /Create New Location/i });
    const rejectButton = getByRole('button', { name: /Reject Contribution/i });
    const claimButton = getByRole('button', { name: /Go to Claim/i });

    expect(createButton).toBeDisabled();
    expect(rejectButton).toBeDisabled();
    expect(claimButton).toBeDisabled();
  });

  test('should enable button when fetching is false', async () => {
    const { getByRole } = renderComponent(
      {
        dashboardContributionRecord: {
          singleModerationEvent: {
            fetching: false
          }
        }
      }
    );
    const createButton = getByRole('button', { name: /Create New Location/i });
    const rejectButton = getByRole('button', { name: /Reject Contribution/i  });
    const claimButton = getByRole('button', { name: /Go to Claim/i });

    await waitFor(() => {
      expect(createButton).not.toBeDisabled();
      expect(rejectButton).not.toBeDisabled();
      expect(claimButton).not.toBeDisabled();
    });

  });

  test('renders the "No potential matches found" block if no potential matches', () => {
    const { getByText } = renderComponent();

    expect(getByText('No potential matches found')).toBeInTheDocument();
  });

  test('renders the loading spinner', () => {
    const {getByRole} = renderComponent(
      {
        dashboardContributionRecord: {
          singleModerationEvent: {
            fetching: true
          }
        }
      }
    );

    expect(getByRole('progressbar')).toBeInTheDocument();
  });

  test('should render event data when provided', async () => {
    const { container, reduxStore } = renderComponent(preloadedState);

    await waitFor(() => {
      const moderationResponseObjectElement = container.querySelector("pre");
      expect(moderationResponseObjectElement).toBeInTheDocument();
    });

    const res = reduxStore.getState().dashboardContributionRecord.singleModerationEvent.data;
    expect(Object.keys(res).length).toBe(12);
  });

  test('should render potential matches when available', () => {
    const matches = {
      data: [
        {
            "name": "Changzhou Hualida Garments Group Co.",
            "claim_status": "unclaimed",
            "sector": [
                "Apparel"
            ],
            "country": {
                "name": "China",
                "alpha_2": "CN",
                "alpha_3": "CHN",
                "numeric": "156"
            },
            "address": "Lot 303 No.1108 Zhongwu High Road Changzhou Jiangsu China - China",
            "os_id": "CN2024351RXE7HX",
            "coordinates": {
                "lat": 31.750302,
                "lng": 119.96891
            }
        },
        {
            "name": "Changzhou Hualida Garments Group Co.",
            "claim_status": "unclaimed",
            "sector": [
                "Apparel"
            ],
            "country": {
                "name": "China",
                "alpha_2": "CN",
                "alpha_3": "CHN",
                "numeric": "156"
            },
            "address": "Lot 303 No.1108 Zhongwu High Road Changzhou Jiangsu China - China",
            "os_id": "CN2024353Z74V5E",
            "coordinates": {
                "lat": 31.750302,
                "lng": 119.96891
            }
        },
        {
            "name": "Changzhou Hualida Garments Group Co.",
            "claim_status": "unclaimed",
            "sector": [
                "Apparel"
            ],
            "country": {
                "name": "China",
                "alpha_2": "CN",
                "alpha_3": "CHN",
                "numeric": "156"
            },
            "address": "Lot 303 No.1108 Zhongwu High Road Changzhou Jiangsu China - China",
            "os_id": "CN20243513WN976",
            "coordinates": {
                "lat": 31.750302,
                "lng": 119.96891
            }
        },
      ],
    };
  
    const { reduxStore } = renderComponent();
    reduxStore.dispatch(completeFetchPotentialMatches(matches));

    const res = reduxStore.getState().dashboardContributionRecord.potentialMatches.matches
    expect(res.length).toBe(3);
  });
});
