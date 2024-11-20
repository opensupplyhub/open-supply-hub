import React from 'react';
import ContributeList from '../../components/Contribute';
import { render} from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from "react-redux";
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'

describe('SubmitListUploadingButton component without DISABLE_LIST_UPLOADING', () => {
    const middlewares = [thunk];
    const mockStore = configureMockStore(middlewares);
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
                "id": 3648,
                "name": "Clothes",
                "description": "Nessa Drew",
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
        featureFlags: { flags:features,fetching:false, fetchingFeatureFlags:false },
        embeddedMap: { isEmbeded:false },
        fetching:false,
        error: null,
        fetchingFacilityLists:false,
        // updateName: ()=>{},
        // updateDescriptio: ()=>{},
        // updateListToReplace:  ()=>{},
        // uploadList:()=>{},
        // fetchLists: ()=>{},
        // resetForm:  ()=>{},
    };
    const preloadedState = {
        userHasSignedIn: true,
        fetchingSessionSignIn: false,
      };
    const store = mockStore(initialState);

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
    const middlewares = [thunk];
    const mockStore = configureMockStore(middlewares);
    const features = {
        disable_list_uploading: true,
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
                "id": 3648,
                "name": "Clothes",
                "description": "Nessa Drew",
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
        featureFlags: { flags:features,fetching:false, fetchingFeatureFlags:false },
        embeddedMap: { isEmbeded:false },
        fetching:false,
        error: null,
        fetchingFacilityLists:false,
        // updateName: ()=>{},
        // updateDescriptio: ()=>{},
        // updateListToReplace:  ()=>{},
        // uploadList:()=>{},
        // fetchLists: ()=>{},
        // resetForm:  ()=>{},
    };
    const preloadedState = {
        userHasSignedIn: true,
        fetchingSessionSignIn: false,
      };
    const store = mockStore(initialState);

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
        const {getByText} = renderComponent();
        const button = getByText('SUBMIT').closest('button');

        expect(button).toBeInTheDocument();
        expect(button).toHaveAttribute('disabled');
        expect(button).toBeDisabled();
    });
});

