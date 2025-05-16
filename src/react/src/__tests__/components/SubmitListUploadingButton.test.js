import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from "react-redux";
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'

import ContributeList from '../../components/ContributeList';
import { MAINTENANCE_MESSAGE } from '../../util/constants';

jest.mock('@material-ui/core/Popper', () => ({ children }) => children);
jest.mock('@material-ui/core/Portal', () => ({ children }) => children);

afterEach(() => {
    jest.resetAllMocks();
});

const createMockStore = (featureFlags, baseState) => {
    const middlewares = [thunk];
    const mockStore = configureMockStore(middlewares);

    return mockStore({
      ...baseState,
      featureFlags: {
        flags: featureFlags,
        fetching: false,
        fetchingFeatureFlags: false
      }
    });
};

describe('SubmitListUploadingButton component without DISABLE_LIST_UPLOADING', () => {
    const features = {
        disable_list_uploading: false,
    };

    const user = {
        id: 57658,
        email: '',
        isModerationMode: false,
        name: '',
        description: '',
        website: '',
        contributorType: '',
        otherContributorType: '',
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
        facilityLists: [],
    };
    const initialState = {
        auth: {
            user: { user },
            session: { fetching: false },
        },
        upload: {
            form: { name:'', description:'', filename:'', replaces:0 },
            fetching: false,
            error: null,
        },
        facilityLists: { facilityLists: [
            {
                "id": 8573,
                "name": "Apparel",
                "description": "Test description",
                "file_name": "Template_Excel.xlsx",
                "is_active": false,
                "is_public": true,
                "item_count": 0,
                "items_url": "/api/facility-lists/8573/items/",
                "statuses": [],
                "status_counts": {
                    "UPLOADED": 1,
                    "PARSED": 1,
                    "GEOCODED": 1,
                    "GEOCODED_NO_RESULTS": 1,
                    "MATCHED": 1,
                    "POTENTIAL_MATCH": 1,
                    "CONFIRMED_MATCH": 1,
                    "ERROR": 1,
                    "ERROR_PARSING": 1,
                    "ERROR_GEOCODING": 1,
                    "ERROR_MATCHING": 1,
                    "DUPLICATE": 1,
                    "DELETED": 1,
                    "ITEM_REMOVED": 1
                },
                "contributor_id": 2371,
                "created_at": "2024-01-13T10:12:05.895143Z",
                "match_responsibility": "moderator",
                "status": "AUTOMATIC",
                "status_change_reason": "test",
                "file": "/Template_Excel_KdIAiX9.xlsx",
                "parsing_errors": []
            },],
            fetchingFacilityLists: false,},
            embeddedMap: { isEmbeded:true },
            fetching:false,
            error: null,
            fetchingFacilityLists:false,
        };
    const newPreloadedState = {
        userHasSignedIn: true,
        fetchingSessionSignIn: false,
      };
    const store = createMockStore(features, initialState);

    const renderComponent = (props = {}) =>
        render(
        <Provider store={store}>
            <Router>
                <ContributeList {...newPreloadedState} {...props}/>
            </Router>,
        </Provider>
    );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("renders without crashing", () => {
        renderComponent();
    });

    test('should render the SUBMIT Button when activeFeatureFlags NOT include DISABLE_LIST_UPLOADING',async () => {
        const {getByRole} = renderComponent();

        const button = getByRole('button', { name: 'SUBMIT' });

        expect(button).toBeInTheDocument();
        expect(button).not.toHaveAttribute('disabled');
        expect(button).not.toBeDisabled();
    });
});

describe('SubmitListUploadingButton component with DISABLE_LIST_UPLOADING', () => {
    const features = {
        extended_profile: true,
        disable_list_uploading: true,
    };
    const user = {
        id: 96565,
        email: 'test@gmail.com',
        isModerationMode: true,
        name: 'TestName',
        description: 'test description',
        website: 'https://test.pl',
        contributorType: 'test type',
        otherContributorType: 'new type',
        currentPassword: 'pass',
        newPassword: 'pass1',
        confirmNewPassword: 'pass1',
        facilityLists: [],
    };
    const initialState = {
        auth: {
            user: { user },
            session: { fetching: false },
        },
        upload: {
            form: { name:'List name', description:'List description', filename:'file name', replaces:1 },
            fetching: false,
            error: null,
        },
        facilityLists: { facilityLists: [
            {
                "id": 3648,
                "name": "Clothes",
                "description": "No description",
                "file_name": "OSHub_Data_Template_Excel.xlsx",
                "is_active": false,
                "is_public": true,
                "item_count": 0,
                "items_url": "/api/facility-lists/3648/items/",
                "statuses": [],
                "status_counts": {
                    "UPLOADED": 0,
                    "PARSED": 0,
                    "GEOCODED": 0,
                    "GEOCODED_NO_RESULTS": 0,
                    "MATCHED": 0,
                    "POTENTIAL_MATCH": 0,
                    "CONFIRMED_MATCH": 0,
                    "ERROR": 0,
                    "ERROR_PARSING": 0,
                    "ERROR_GEOCODING": 0,
                    "ERROR_MATCHING": 0,
                    "DUPLICATE": 0,
                    "DELETED": 0,
                    "ITEM_REMOVED": 0
                },
                "contributor_id": 7742,
                "created_at": "2024-01-24T11:22:05.895943Z",
                "match_responsibility": "moderator",
                "status": "REJECTED",
                "status_change_reason": "",
                "file": "/OSHub_Data_Template_Excel_KdIAiX9.xlsx",
                "parsing_errors": []
            },],
            fetchingFacilityLists: false,},
        embeddedMap: { isEmbeded:false },
        fetching:false,
        error: null,
        fetchingFacilityLists:false,
    };
    const preloadedState = {
        userHasSignedIn: true,
        fetchingSessionSignIn: false,
      };
    const store = createMockStore(features, initialState);

    const renderComponent = (props = {}) =>
        render(
        <Provider store={store}>
            <Router>
                <ContributeList {...preloadedState} {...props}/>
            </Router>,
        </Provider>
    );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('should render the disabled SUBMIT Button when activeFeatureFlags include DISABLE_LIST_UPLOADING', () => {
        const {getByRole} = renderComponent();
        const submitButton = getByRole('button', { name: 'SUBMIT' });

        expect(submitButton).toBeInTheDocument();
        expect(submitButton).toHaveAttribute('disabled');
        expect(submitButton).toBeDisabled();
    });

    test('shows tooltip on hover SUBMIT Button', async () => {
        const {getByRole} = renderComponent();
        const button = getByRole('button', { name:'SUBMIT' });

        expect(button).toHaveTextContent('SUBMIT');
        expect(button).toBeDisabled();

        const noTooltipElement = document.querySelector(`[title="${
            MAINTENANCE_MESSAGE}"]`);

        expect(noTooltipElement).toBeInTheDocument();
        fireEvent.mouseOver(button);

        const tooltip = document.querySelector('[aria-describedby^="mui-tooltip-"]');

        expect(tooltip).toBeInTheDocument();
        fireEvent.mouseOut(button);

        const noTooltipElementAfter = document.querySelector(`[title="${
            MAINTENANCE_MESSAGE}"]`);

        expect(noTooltipElementAfter).toBeInTheDocument();
      });
});
