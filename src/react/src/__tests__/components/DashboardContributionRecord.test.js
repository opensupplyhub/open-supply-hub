import React from 'react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import { waitFor, fireEvent } from '@testing-library/react';
import DashboardContributionRecord from '../../components/Dashboard/DashboardContributionRecord';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
  fetchSingleModerationEvent,
  fetchPotentialMatches,
  fetchExistingOsIdLocation,
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
    fetchExistingOsIdLocation: jest.fn(),
  };
});

jest.mock('../../components/Dashboard/RejectModerationEventDialog', () => ({
  __esModule: true,
  default: ({ isOpenDialog, closeDialog }) => (
    <div>
      {isOpenDialog && (
        <button type="button" onClick={closeDialog}>
          Close Dialog
        </button>
      )}
    </div>
  ),
}));

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
      existingOsIdLocation: {
        data: null,
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
            existingOsIdLocation: {
              ...preloadedState.dashboardContributionRecord.existingOsIdLocation,
              ...stateOverrides.dashboardContributionRecord?.existingOsIdLocation,
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
    fetchExistingOsIdLocation.mockReturnValue(() => Promise.resolve());
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

  test('opens the RejectModerationEventDialog when the Reject Contribution button is clicked', () => {
    const { getByRole } = renderComponent();

    const rejectButton = getByRole('button', { name: /Reject Contribution/i });
    fireEvent.click(rejectButton);

    expect(getByRole('button', { name: /Close Dialog/i })).toBeInTheDocument();
  });

  test('closes the RejectModerationEventDialog when the close button is clicked', () => {
    const { getByRole, queryByText } = renderComponent();

    const rejectButton = getByRole('button', { name: /Reject Contribution/i });
    fireEvent.click(rejectButton);

    const closeButton = getByRole('button', { name: /Close Dialog/i });
    fireEvent.click(closeButton);

    expect(queryByText('Close Dialog')).not.toBeInTheDocument();
  });

  test('does not render the Existing OSID section for a CREATE request', () => {
    const { queryByText } = renderComponent({
      dashboardContributionRecord: {
        singleModerationEvent: {
          data: { ...data, request_type: 'CREATE' },
        },
      },
    });

    expect(queryByText('Existing OSID')).not.toBeInTheDocument();
  });

  const existingOsIdState = {
    dashboardContributionRecord: {
      singleModerationEvent: {
        data: { ...data, os_id: 'CN2021250D1DTU7', request_type: 'UPDATE' },
      },
      existingOsIdLocation: {
        fetching: false,
        error: null,
        data: {
          os_id: 'CN2021250D1DTU7',
          name: 'Existing Facility Name',
          address: '123 Existing St',
          claim_status: 'unclaimed',
        },
      },
    },
  };

  test('renders the Existing OSID section with location data for an UPDATE request', () => {
    const { getByText } = renderComponent(existingOsIdState);

    expect(getByText('Existing OSID')).toBeInTheDocument();
    expect(getByText('CN2021250D1DTU7')).toBeInTheDocument();
    expect(getByText('Name: Existing Facility Name')).toBeInTheDocument();
    expect(getByText('Address: 123 Existing St')).toBeInTheDocument();
    expect(getByText('Claimed Status: unclaimed')).toBeInTheDocument();
  });

  test('renders a Confirm button in the Existing OSID section for a pending UPDATE event', () => {
    const { getAllByRole } = renderComponent(existingOsIdState);

    const confirmButtons = getAllByRole('button', { name: /Confirm/i });
    expect(confirmButtons.length).toBeGreaterThanOrEqual(1);
  });

  test('calls confirmPotentialMatch with the existing OS ID when Confirm is clicked in Existing OSID section', async () => {
    const { getAllByRole } = renderComponent(existingOsIdState);

    const confirmButtons = getAllByRole('button', { name: /Confirm/i });
    fireEvent.click(confirmButtons[0]);

    await waitFor(() => {
      expect(confirmPotentialMatchFromModerationEvent).toHaveBeenCalledWith(
        expect.anything(),
        'CN2021250D1DTU7',
      );
    });
  });

  test('shows "Confirm" (not "Matched") in Existing OSID section when event is REJECTED', () => {
    const { queryByText } = renderComponent({
      dashboardContributionRecord: {
        singleModerationEvent: {
          data: {
            ...data,
            os_id: 'CN2021250D1DTU7',
            request_type: 'UPDATE',
            status: 'REJECTED',
          },
        },
        existingOsIdLocation: {
          fetching: false,
          error: null,
          data: {
            os_id: 'CN2021250D1DTU7',
            name: 'Existing Facility Name',
            address: '123 Existing St',
            claim_status: 'unclaimed',
          },
        },
      },
    });

    expect(queryByText('Matched')).not.toBeInTheDocument();
  });

  test('calls fetchExistingOsIdLocation when request_type is UPDATE and os_id is present', async () => {
    renderComponent({
      dashboardContributionRecord: {
        singleModerationEvent: {
          data: { ...data, os_id: 'CN2021250D1DTU7', request_type: 'UPDATE' },
        },
      },
    });

    await waitFor(() => {
      expect(fetchExistingOsIdLocation).toHaveBeenCalledWith('CN2021250D1DTU7');
    });
  });

  test('does not call fetchExistingOsIdLocation for a CREATE request', async () => {
    renderComponent({
      dashboardContributionRecord: {
        singleModerationEvent: {
          data: { ...data, os_id: null, request_type: 'CREATE' },
        },
      },
    });

    await waitFor(() => {
      expect(fetchSingleModerationEvent).toHaveBeenCalled();
    });

    expect(fetchExistingOsIdLocation).not.toHaveBeenCalled();
  });
});
