import React from 'react';
import DashboardContributionRecord from '../../components/Dashboard/DashboardContributionRecord';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('DashboardContributionRecord component', () => {
  const routeProps = {
    match: {
        params: {
            moderationID: '1',
        },
    },
  };
  const defaultProps = {
    event: {},
    potentialMatches: [],
    error: null,
    fetchPotentialMatchError: null,
  };

  const renderComponent = (props = {}) => renderWithProviders(
    <DashboardContributionRecord {...defaultProps} {...routeProps} {...props}/>
  );

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render the CreateButton', () => {
    const {getByText} = renderComponent();

    expect(getByText('Create New Location')).toBeInTheDocument();
  });

  test('should render the RejectButton', () => {
    const {getByText} = renderComponent();

    expect(getByText('Reject Contribution')).toBeInTheDocument();
  });

  test('should render the ClaimButton', () => {
    const {getByText} = renderComponent();

    expect(getByText('Go to Claim')).toBeInTheDocument();
  });

  test('should disable button when fetching is true', () => {
    const {getByRole} = renderComponent({ fetching: true });
    const createButton = getByRole('button', { name: /Create New Location/i });
    const rejectButton = getByRole('button', { name: /Reject Contribution/i });
    const claimButton = getByRole('button', { name: /Go to Claim/i });

    expect(createButton).toBeDisabled();
    expect(rejectButton).toBeDisabled();
    expect(claimButton).toBeDisabled();
  });

  test('should enable button when fetching is false', () => {
    const {getByRole} = renderComponent({fetching: false,moderationID :'2'});
    const createButton = getByRole('button', { name: /Create New Location/i });
    const rejectButton = getByRole('button', { name: /Reject Contribution/i  });
    const claimButton = getByRole('button', { name: /Go to Claim/i });

    expect(createButton.getAttribute("disabled")).toBe('');
    expect(rejectButton.getAttribute("disabled")).toBe('');
    expect(claimButton.getAttribute("disabled")).toBe('');
  });

  test('renders the "No potential matches found" block if no potential matches', () => {
    const {getByText} = renderComponent();

    expect(getByText('No potential matches found')).toBeInTheDocument();
  });


  it('renders the loading spinner', () => {
    const {getByRole} = renderComponent({ fetching: true });

    expect(getByRole('progressbar')).toBeInTheDocument();
  });


});
