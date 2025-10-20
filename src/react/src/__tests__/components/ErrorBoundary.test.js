// Mock the util module FIRST, before any imports
jest.mock('../../util/util', () => ({
	...jest.requireActual('../../util/util'),
	logErrorToRollbar: jest.fn(),
}))

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
})

// Now import everything AFTER the mocks are set up
import React from 'react'
import { waitFor } from '@testing-library/react'
import FacilityLists from '../../components/FacilityLists'
import ErrorBoundary from '../../components/ErrorBoundary'
import { USER_DEFAULT_STATE } from '../../util/constants'
import renderWithProviders from '../../util/testUtils/renderWithProviders'

// Import util and get reference to the mocked function
const util = require('../../util/util')
const mockLogErrorToRollbar = util.logErrorToRollbar

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
	beforeEach(() => {
		mockLogErrorToRollbar.mockClear()
	})

	it('logs to Rollbar on window error events', async () => {
		const user = { ...USER_DEFAULT_STATE, isAnon: false, id: 5, contributor_id: 123 }

		// Suppress console output
		const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

		// Capture registered listeners
		const listeners = {}
		const originalAddEventListener = window.addEventListener.bind(window)
		const addEventListenerSpy = jest
			.spyOn(window, 'addEventListener')
			.mockImplementation((type, cb, options) => {
				listeners[type] = cb
				return originalAddEventListener(type, cb, options)
			})

		// eslint-disable-next-line global-require
		const { useGlobalErrorHandler } = require('../../util/hooks')
		// eslint-disable-next-line global-require
		const { render } = require('@testing-library/react')

		const GlobalErrorHandlerTester = ({ user: testUser }) => {
			useGlobalErrorHandler(testUser)
			return null
		}

		render(<GlobalErrorHandlerTester user={user} />)

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

		// logErrorToRollbar is called synchronously
		expect(mockLogErrorToRollbar).toHaveBeenCalled()
		expect(mockLogErrorToRollbar).toHaveBeenCalledWith(
			expect.objectContaining({ addEventListener: expect.any(Function) }),
			expect.objectContaining({ message: 'Global handler test error' }),
			user
		)

		consoleSpy.mockRestore()
		addEventListenerSpy.mockRestore()
	})
})
