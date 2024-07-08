import React, { useEffect } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import Grid from '@material-ui/core/Grid';

import ControlledTextInput from './ControlledTextInput';
import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import Button from './Button';
import ShowOnly from './ShowOnly';
import SendResetPasswordEmailForm from './SendResetPasswordEmailForm';
import TogglePassswordField from './TogglePassswordField';

import {
    updateLoginFormEmailAddress,
    updateLoginFormPassword,
    submitLoginForm,
    resetAuthFormState,
} from '../actions/auth';

import {
    getValueFromEvent,
    makeSubmitFormOnEnterKeyPressFunction,
} from '../util/util';

import { userPropType } from '../util/propTypes';

import {
    authRegisterFormRoute,
    facilitiesRoute,
    USER_DEFAULT_STATE,
} from '../util/constants';

import { formValidationErrorMessageStyle } from '../util/styles';

const LOGIN_EMAIL = 'LOGIN_EMAIL';
const LOGIN_PASSWORD = 'LOGIN_PASSWORD';

const LoginForm = ({
    history,
    user,
    email,
    password,
    fetching,
    sessionFetching,
    error,
    updateEmail,
    updatePassword,
    submitForm,
    submitFormOnEnterKeyPress,
    clearForm,
}) => {
    useEffect(() => {
        if (!user.isAnon) {
            if (history.location.state?.prevPath) {
                history.push(history.location.state.prevPath);
            } else {
                history.push(facilitiesRoute);
            }
        }
    }, [user]);

    useEffect(
        () => () => {
            clearForm();
        },
        [],
    );

    if (sessionFetching) {
        return null;
    }

    return (
        <AppOverflow>
            <AppGrid title="Log In" style={{ marginBottom: '100px' }}>
                <Grid item xs={12} sm={7}>
                    <p>
                        You must be a registered user to contribute to Open
                        Supply Hub.
                        <br />
                        Don&apos;t have an account?{' '}
                        <Link
                            to={authRegisterFormRoute}
                            href={authRegisterFormRoute}
                            className="link-underline"
                        >
                            Register
                        </Link>
                        .
                    </p>
                    <div className="form__field">
                        <label className="form__label" htmlFor={LOGIN_EMAIL}>
                            Email Address
                        </label>
                        <ControlledTextInput
                            autoFocus
                            id={LOGIN_EMAIL}
                            type="email"
                            value={email}
                            onChange={updateEmail}
                            submitFormOnEnterKeyPress={
                                submitFormOnEnterKeyPress
                            }
                        />
                    </div>
                    <TogglePassswordField
                        id={LOGIN_PASSWORD}
                        value={password}
                        lable="Passowrd"
                        updatePassword={updatePassword}
                        submitFormOnEnterKeyPress={submitFormOnEnterKeyPress}
                    />
                    <SendResetPasswordEmailForm />
                    <ShowOnly when={!!(error && error.length)}>
                        <ul style={formValidationErrorMessageStyle}>
                            {error && error.length
                                ? error.map(err => <li key={err}>{err}</li>)
                                : null}
                        </ul>
                    </ShowOnly>
                    <Button
                        text="Log In"
                        onClick={submitForm}
                        disabled={fetching}
                    />
                </Grid>
            </AppGrid>
        </AppOverflow>
    );
};

LoginForm.defaultProps = {
    error: null,
    user: USER_DEFAULT_STATE,
};

LoginForm.propTypes = {
    email: string.isRequired,
    password: string.isRequired,
    fetching: bool.isRequired,
    error: arrayOf(string.isRequired),
    updateEmail: func.isRequired,
    updatePassword: func.isRequired,
    submitForm: func.isRequired,
    submitFormOnEnterKeyPress: func.isRequired,
    clearForm: func.isRequired,
    user: userPropType,
    history: shape({
        push: func.isRequired,
    }).isRequired,
    sessionFetching: bool.isRequired,
};

const mapStateToProps = ({
    auth: {
        login: {
            form: { email, password },
        },
        user: { user },
        session: { fetching: sessionFetching },
        fetching,
        error,
    },
}) => ({
    email,
    password,
    fetching,
    error,
    user,
    sessionFetching,
});

const mapDispatchToProps = dispatch => ({
    updateEmail: e =>
        dispatch(updateLoginFormEmailAddress(getValueFromEvent(e))),
    updatePassword: e =>
        dispatch(updateLoginFormPassword(getValueFromEvent(e))),
    submitForm: () => dispatch(submitLoginForm()),
    clearForm: () => dispatch(resetAuthFormState()),
    submitFormOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(() =>
        dispatch(submitLoginForm()),
    ),
});

export default connect(mapStateToProps, mapDispatchToProps)(LoginForm);
