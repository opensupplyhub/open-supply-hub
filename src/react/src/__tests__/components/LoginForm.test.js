import React from 'react';
import { Router, Route } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';

import LoginForm from './../../components/LoginForm';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import history from '../../util/history';
import { completeSubmitLoginForm } from '../../actions/auth';
import { authLoginFormRoute } from '../../util/constants';

describe('LoginForm component', () => {
    test('redirects to the previous page if that page has been provided while following login page', async () => {
        const loginWarningMessage = /You must be a registered user to contribute to Open Supply Hub\./;
        const previousPath = '/previous-page';
        const browserHistoryLocationState = { prevPath: previousPath };

        const {reduxStore} = renderWithProviders(
            <Router history={history}>
                <Route
                    exact
                    path={authLoginFormRoute}
                    component={LoginForm}
                />
            </Router>
        )
        history.push(
            authLoginFormRoute,
            {
                ...browserHistoryLocationState
            }
        );

        expect(screen.queryByText(loginWarningMessage)).toBeInTheDocument()

        const validCompleteSubmitLoginFormPayload = {
            'id': 8889,
            'email': 'myemail@gmail.com',
            'name': 'New Organization',
            'description': 'Lorem ipsum dolor',
            'website': '',
            'contributor_type': 'Brand / Retailer',
            'other_contributor_type': '',
            'contributor_id': 8858,
            'embed_config': {
              'width': '',
              'height': '',
              'color': '',
              'font': '',
              'prefer_contributor_name': false,
              'text_search_label': '',
              'map_style': '',
              'hide_sector_data': false
            },
            'claimed_facility_ids': {
              'pending': [],
              'approved': []
            },
            'embed_level': null,
            'last_login': '2024-04-29T10:36:58.446660Z',
            'is_superuser': true,
            'is_staff': true,
            'is_active': true,
            'is_moderation_mode': false,
            'username': null,
            'should_receive_newsletter': false,
            'has_agreed_to_terms_of_service': true,
            'created_at': '2024-04-25T10:22:45.901048Z',
            'updated_at': '2024-04-25T10:22:47.268510Z',
            'burst_rate': '100/minute',
            'sustained_rate': '10000/day',
            'data_upload_rate': '30/minute',
            'groups': [],
            'user_permissions': [],
            'allowed_records_number': 10000,
        }
        reduxStore.dispatch(
            completeSubmitLoginForm(validCompleteSubmitLoginFormPayload)
        );

        await waitFor(() => {
            expect(history.location.pathname).toBe(previousPath);
          });

        expect(screen.queryByText(loginWarningMessage)).not.toBeInTheDocument()
    });
});

