import React, { useState } from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import DashboardClaimsDetailsControls from '../../components/DashboardClaimDetailsControls';
import { Provider } from 'react-redux';
import { store } from '../../configureStore';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

describe('DashboardClaimsDetailsControls', () => {
  const defaultProps = {
    data: {
      id: 1,
      status: 'PENDING',
      created_at: '2020-01-01T00:00:00Z',
      updated_at: '2020-01-01T00:00:00Z',
      contact_person: 'John Doe',
      job_title: 'Manager',
      email: 'john@gmail.com',
      phone_number: '123-456-7890',
      company_name: 'Test Company',
      website: 'http://www.test.com',
      facility_description: 'Test description',
      linkedin_profile: 'http://www.linkedin.com',
      contributor: {},
      facility: {
        id: '1',
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [-122.4194, 37.7749],
        },
        properties: {
          name: 'Test Facility',
          address: '123 Test St',
          country_code: 'US',
          country_name: 'United States',
        },
      },
      status_change: {
        status_change_by: '',
        status_change_date: '2020-01-01T00:00:00Z',
        status_change_reason: '',
      },
      notes: [
        {
          id: 1,
          note: 'Test note',
          created_at: '2020-01-01T00:00:00Z',
          updated_at: '2020-01-01T00:00:00Z',
        },
      ],
      attachments: [
        {
         file_name: 'test.pdf',
         claim_attachment: 'test.pdf',
        },
      ],




    },
    fetching: false,
    error: null,
    messageClaimant: jest.fn(),
    approveClaim: jest.fn(),
    denyClaim: jest.fn(),
    revokeClaim: jest.fn(),
  };

  let initialState

  beforeEach(() => {
    initialState = mockStore({
      claimFacilityDashboard : {
        statusControls: {
            fetching: false,
            error: null
        },
        note: {
            note: "",
            fetching: false,
            error: null
        }
      }
    })
  })  

  test('renders without crashing', () => {
    render(
      <Provider store={initialState}>
        <DashboardClaimsDetailsControls {...defaultProps} />
      </Provider>
    );
  });

  test('renders correct buttons for pending status', () => {
    const { getByText, queryByText } = render(
      <Provider store={initialState}>
        <DashboardClaimsDetailsControls {...defaultProps} />
      </Provider>
    );
    expect(getByText('Message Claimant')).toBeInTheDocument();
    expect(getByText('Approve Claim')).toBeInTheDocument();
    expect(getByText('Deny Claim')).toBeInTheDocument();
    expect(queryByText('Revoke Claim')).not.toBeInTheDocument();
  });

  test('renders correct button for approved status', () => {
    const props = {
      ...defaultProps,
      data: { ...defaultProps.data, status: 'APPROVED' },
    };
    const { getByText, queryByText } = render(
      <Provider store={initialState}>
        <DashboardClaimsDetailsControls {...props} />
      </Provider>
    );
    expect(getByText('Revoke Claim')).toBeInTheDocument();
    expect(queryByText('Message Claimant')).not.toBeInTheDocument();
    expect(queryByText('Approve Claim')).not.toBeInTheDocument();
    expect(queryByText('Deny Claim')).not.toBeInTheDocument();
  });

  test('opens and closes dialog', async () => {
    const { getByText, getByLabelText, queryByText } = render(
      <Provider store={initialState}>
        <DashboardClaimsDetailsControls {...defaultProps} />
      </Provider>
    );
    fireEvent.click(getByText('Message Claimant'));
    expect(getByText('Send a message to claimant?')).toBeInTheDocument();
    expect(getByLabelText('Enter a message. (This will be emailed to the contact email associated with this claim.)')).toBeInTheDocument();
    fireEvent.click(getByText('Cancel'));
    await waitFor(() => {
      expect(queryByText('Send a message to claimant?')).not.toBeInTheDocument();
    });
  });

  test('updates message to claimant text', async () => {
    const { getByText, getByLabelText } = render(
      <Provider store={initialState}>
        <DashboardClaimsDetailsControls {...defaultProps} />
      </Provider>
    );
    fireEvent.click(getByText('Message Claimant'));
    const input = getByLabelText('Enter a message. (This will be emailed to the contact email associated with this claim.)');
    fireEvent.change(input, { target: { value: 'Message to claimant.' } });
    expect(input.value).toBe('Message to claimant.');
  });
});
