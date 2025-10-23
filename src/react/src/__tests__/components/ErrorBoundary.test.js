import React from 'react'
import { waitFor } from '@testing-library/react'
import { shape } from 'prop-types'
import FacilityLists from '../../components/FacilityLists'
import ErrorBoundary from '../../components/ErrorBoundary'
import { USER_DEFAULT_STATE } from '../../util/constants'
import renderWithProviders from '../../util/testUtils/renderWithProviders'
import * as util from '../../util/util'

const ERROR_MESSAGE = 'Error while fetching facilities'
const CONTRIBUTOR_ID = 1705

// Mock the util module
jest.mock('../../util/util', () => ({
	...jest.requireActual('../../util/util'),
	logErrorToRollbar: jest.fn(),
}))

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

// Get reference to the mocked function
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
	let logErrorToRollbarSpy;

	afterEach(() => {
		consoleSpy.mockRestore();
		logErrorToRollbarSpy.mockRestore();
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

		logErrorToRollbarSpy = jest.spyOn(util, 'logErrorToRollbar').mockImplementation((window, error, user) => {
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
		expect(logErrorToRollbarSpy).toHaveBeenCalled();
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

		logErrorToRollbarSpy = jest.spyOn(util, 'logErrorToRollbar').mockImplementation((window, error, user) => {
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
		expect(logErrorToRollbarSpy).toHaveBeenCalled();
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

		/* 
		We need to import these after mocking window.addEventListener
		so the hook and render function use the mocked version
		*/
		// eslint-disable-next-line global-require
		const { useGlobalErrorHandler } = require('../../util/hooks')
		// eslint-disable-next-line global-require
		const { render } = require('@testing-library/react')

		const GlobalErrorHandlerTester = ({ user: testUser }) => {
			useGlobalErrorHandler(testUser)
			return null
		}

		GlobalErrorHandlerTester.propTypes = {
			user: shape({}).isRequired,
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
