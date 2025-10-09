import React from 'react'
import FacilityLists from '../../components/FacilityLists'
import ErrorBoundary from '../../components/ErrorBoundary'
import { USER_DEFAULT_STATE } from '../../util/constants'
import renderWithProviders from '../../util/testUtils/renderWithProviders'
import * as util from '../../util/util'
import { waitFor } from '@testing-library/react'

const ERROR_MESSAGE = 'Error while fetching facilities'
const CONTRIBUTOR_ID = 1705

jest.mock('../../components/FacilityLists', () => {
	const { Component } = jest.requireActual('react');

	/* eslint-disable react/prefer-stateless-function */
	class MockedFacilityLists extends Component {
		/* eslint-disable react/require-render-return */
		render() {
			throw new Error(ERROR_MESSAGE);
		}
	}

	return MockedFacilityLists;
});

const mockLogErrorToRollbarGetUserInfo = (user, shouldApiUser) => {
	expect(user.contributor_id).toBe(CONTRIBUTOR_ID)
	const userType = util.isApiUser(user) ? 'API user' : 'User';
	if (shouldApiUser) {
		expect(userType).toBe('API user')
	} else {
		expect(userType).toBe('User')
	}
}

describe('Test ErrorBoundary component for API user with contributor id', () => {
	let consoleSpy;
	let mockLogErrorToRollbar;

	afterEach(() => {
		consoleSpy.mockRestore();
		mockLogErrorToRollbar.mockRestore();
	});

	it('Displays an error message on error in FacilityLists for Api user', () => {
		const preloadedState = {
			auth: {
				user: {
					user: { ...USER_DEFAULT_STATE,
						isAnon: false,
						contributor_id: CONTRIBUTOR_ID,
						groups: [1, 2]
						},
					},
			},
		}

		mockLogErrorToRollbar = jest.spyOn(util, 'logErrorToRollbar').mockImplementation((window, error, user) => {
			mockLogErrorToRollbarGetUserInfo(user, true)
		});
		// Suppress console.error() invocations during test runtime to avoid redundant output in the console.
		consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

		const { container } = renderWithProviders(
			<ErrorBoundary>
				<FacilityLists />
			</ErrorBoundary>
			,
			{ preloadedState }
		)

		const errorDivElement = atob(container.querySelector('.notranslate').textContent);
		expect(errorDivElement).toMatch(ERROR_MESSAGE);
		expect(mockLogErrorToRollbar).toHaveBeenCalled();
	})

	it('Displays an error message on error in FacilityLists for regular user', () => {
		const preloadedState = {
			auth: {
				user: {
					user: { ...USER_DEFAULT_STATE,
						isAnon: false,
						contributor_id: CONTRIBUTOR_ID,
						},
					},
			},
		}

		mockLogErrorToRollbar = jest.spyOn(util, 'logErrorToRollbar').mockImplementation((window, error, user) => {
			mockLogErrorToRollbarGetUserInfo(user, false)
		});
		// Suppress console.error() invocations during test runtime to avoid redundant output in the console.
		consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

		const { container } = renderWithProviders(
			<ErrorBoundary>
				<FacilityLists />
			</ErrorBoundary>
			,
			{ preloadedState }
		)

		const errorDivElement = atob(container.querySelector('.notranslate').textContent);
		expect(errorDivElement).toMatch(ERROR_MESSAGE);
		expect(mockLogErrorToRollbar).toHaveBeenCalled();
	})

})

describe('useGlobalErrorHandler', () => {
	it('logs to Rollbar on window error events', async () => {
		const user = { ...USER_DEFAULT_STATE, isAnon: false, contributor_id: 123 }

		// Mock Rollbar on window so the real util.logErrorToRollbar will hit it
		const rollbarError = jest.fn()
		const rollbarConfigure = jest.fn()
		window.Rollbar = { error: rollbarError, configure: rollbarConfigure }

		// Suppress React error output caused by dispatching a window error event
		const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

		// Capture registered listeners so we can invoke them directly without relying on Event
		const listeners = {}
		const addEventListenerSpy = jest
			.spyOn(window, 'addEventListener')
			.mockImplementation((type, cb) => {
				listeners[type] = cb
			})


		// Load the hook module in isolation
		jest.isolateModules(() => {
			const { useGlobalErrorHandler } = require('../../util/hooks')

			const GlobalErrorHandlerTester = ({ user }) => {
				useGlobalErrorHandler(user)
				return null
			}

			renderWithProviders(<GlobalErrorHandlerTester user={user} />)
		})

		await waitFor(() => {
			expect(typeof listeners.error).toBe('function')
		})

		const error = new Error('Global handler test error')
		listeners.error({
			message: error.message,
			filename: 'test.js',
			lineno: 1,
			colno: 1,
			error,
		})

		await waitFor(() => {
			expect(rollbarError).toHaveBeenCalled()
		})

		consoleSpy.mockRestore()
		addEventListenerSpy.mockRestore()
		jest.resetModules()
	})
})
