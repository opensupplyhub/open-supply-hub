import React from 'react';
import DashboardContributionRecord from '../../components/Dashboard/DashboardContributionRecord';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { waitFor } from '@testing-library/react';

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
    fetchEventError: null,
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

  test('should disable button when eventFetching is true', () => {
    const {getByRole} = renderComponent({ eventFetching: true });
    const createButton = getByRole('button', { name: /Create New Location/i });
    const rejectButton = getByRole('button', { name: /Reject Contribution/i });
    const claimButton = getByRole('button', { name: /Go to Claim/i });

    expect(createButton).toBeDisabled();
    expect(rejectButton).toBeDisabled();
    expect(claimButton).toBeDisabled();
  });

  test('should enable button when fetching is false', async () => {
    const {getByRole} = renderComponent({eventFetching: false});
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
    const {getByText} = renderComponent();

    expect(getByText('No potential matches found')).toBeInTheDocument();
  });

  test('renders the loading spinner', () => {
    const {getByRole} = renderComponent({ eventFetching: true });

    expect(getByRole('progressbar')).toBeInTheDocument();
  });

  test('should render event data when provided', async () => {
    const event = {
      moderation_id: 14,
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
      claim_id: 0,
    };
    const { container } = renderComponent({ event });

    await waitFor(() => {
      const preElement = container.querySelector("pre");
      expect(preElement).toBeInTheDocument();
    });
  });


  test('should render potential matches when available', async () => {
    const potentialMatches = [
      {
          os_id: 'CN2031250H1DTN7',
          name: 'Test name INC Test',
          address: '495 Main St, Manhattan, NY - US',
          sector: ['Apparel'],
          parent_company: 'ASI GLOBAL LIMITED',
          product_type: ['Accessories'],
          location_type: [],
          processing_type: ['Final Product Assembly'],
          number_of_workers: {
              min: 0,
              max: 0,
          },
          coordinates: {
              lat: 0,
              lng: 0,
          },
          local_name: '',
          description: '',
          business_url: '',
          minimum_order_quantity: '',
          average_lead_time: '',
          percent_female_workers: 0,
          affiliations: [],
          certifications_standards_regulations: [],
          historical_os_id: [],
          country: {
              name: 'Germany',
              alpha_2: 'DE',
              alpha_3: 'DEU',
              numeric: '276',
          },
          claim_status: 'unclaimed',
      },
    ];
    const {getByText}= renderComponent({potentialMatches});

    await waitFor(() => {
      expect(getByText('Name: Test name INC NEW')).toBeInTheDocument();
      expect(getByText('Address: 1523 Main St, Manhattan, NY - USA')).toBeInTheDocument();
      expect(getByText('Claimed Status: unclaimed')).toBeInTheDocument();
      expect(getByText('Potential Matches (1)')).toBeInTheDocument();
    });
  });
});
