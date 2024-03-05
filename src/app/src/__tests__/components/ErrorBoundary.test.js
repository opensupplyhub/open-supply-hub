import React from 'react';
import { Provider } from 'react-redux';
import { render } from '@testing-library/react';
import configureStore from 'redux-mock-store';
import FacilityLists from '../../components/FacilityLists';
import ErrorBoundary from '../../components/ErrorBoundary';
import { USER_DEFAULT_STATE } from '../../util/constants';
import * as util from '../../util/util';

const ERROR_MESSAGE = 'Error while fetching facilities'
const CONTRIBUTOR_ID = 1705

jest.mock('../../components/FacilityLists', () => {
  const { Component } = jest.requireActual('react');

  class MockedFacilityLists extends Component {
    render() {
      throw new Error(ERROR_MESSAGE);
    }
  }

  return MockedFacilityLists;
});

const mockStore = configureStore([]);

describe('Test ErrorBoundary component for API user with contributor id', () => {
  let initialState;
  let consoleSpy;
  let mockLogErrorToRollbar;

  beforeEach(() => {
    initialState = mockStore({
      auth: {
        user: {
          user: { ...USER_DEFAULT_STATE, 
				isAnon: false, 
				contributor_id: CONTRIBUTOR_ID, 
				groups: [1, 2] 
			},
        },
      },
    });

    mockLogErrorToRollbar = jest.spyOn(util, 'logErrorToRollbar').mockImplementation((window, error, user) => {
		expect(user.contributor_id).toBe(CONTRIBUTOR_ID)
		const userType = util.isApiUser(user) ? 'API user' : 'User';
		expect(userType).toBe('API user')
    });
    // Suppress console.error() invocations during test runtime to avoid redundant output in the console.
    consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    mockLogErrorToRollbar.mockRestore();
  });

  it('Displays an error message on error in FacilityLists', () => {
    const { getByText, container } = render(
      <Provider store={initialState}>
        <ErrorBoundary>
          <FacilityLists />
        </ErrorBoundary>
      </Provider>
    );

	const errorDivElement = atob(container.querySelector('.notranslate').textContent);
	expect(errorDivElement).toMatch(ERROR_MESSAGE);
	expect(mockLogErrorToRollbar).toHaveBeenCalled();
  });
});
