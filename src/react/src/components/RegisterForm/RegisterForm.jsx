import React from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import fromPairs from 'lodash/fromPairs';
import keyBy from 'lodash/keyBy';

import AppGrid from '../AppGrid';
import AppOverflow from '../AppOverflow';
import ShowOnly from '../ShowOnly';
import Button from '../Button';
import RegisterFormField from '../RegisterFormField';

import {
    updateSignUpFormInput,
    submitSignUpForm,
    resetAuthFormState,
} from '../../actions/auth';

import {
    OTHER,
    registrationFieldsEnum,
    registrationFormFields,
    authLoginFormRoute,
} from '../../util/constants';

import {
    registrationFormValuesPropType,
    registrationFormInputHandlersPropType,
} from '../../util/propTypes';

import {
    getStateFromEventForEventType,
    makeSubmitFormOnEnterKeyPressFunction,
} from '../../util/util';

import { formValidationErrorMessageStyle } from '../../util/styles';

import useRegistrationFormSubmit from './hooks';
import s from './styles';

const OSH_DOMAIN = '@opensupplyhub.org';

function RegisterForm({
    fetching,
    error,
    form,
    inputUpdates,
    submitForm,
    submitFormOnEnterKeyPress,
    sessionFetching,
    clearForm,
}) {
    const formSubmitted = useRegistrationFormSubmit(fetching, error, clearForm);

    if (sessionFetching) {
        return null;
    }

    if (formSubmitted) {
        return (
            <AppOverflow>
                <AppGrid title="Registration was successful!">
                    <Grid item xs={12}>
                        <p>
                            Check your email for instructions about how to
                            verify your account.
                        </p>
                        <div style={s.wrapper}>
                            <p style={s.heading}>
                                If you haven&apos;t received the email after 24
                                hours, please follow these steps:
                            </p>
                            <ol style={s.list}>
                                <li style={s.listItem}>
                                    <strong>Check your spam folder:</strong> The
                                    verification email might have been marked as
                                    spam.
                                </li>
                                <li style={s.listItem}>
                                    <strong>Allowlist our domain:</strong> Add{' '}
                                    <strong>{OSH_DOMAIN}</strong> to your email
                                    provider&apos;s safe sender list to prevent
                                    future emails from being blocked or
                                    filtered.
                                </li>
                                <li>
                                    <strong>
                                        Contact your email provider or IT
                                        department:
                                    </strong>{' '}
                                    Ask them to confirm that emails from{' '}
                                    <strong>{OSH_DOMAIN}</strong> are not being
                                    blocked or restricted.
                                </li>
                            </ol>
                        </div>
                    </Grid>
                </AppGrid>
            </AppOverflow>
        );
    }

    const formInputs = registrationFormFields.map((field, index) => (
        <RegisterFormField
            autoFocus={index === 0}
            key={field.id}
            id={field.id}
            label={field.label}
            type={field.type}
            link={field.link}
            hint={field.hint}
            required={field.required}
            options={field.options}
            value={form[field.id]}
            handleChange={inputUpdates[field.id]}
            isHidden={
                form.contributorType !== OTHER &&
                field.id === registrationFieldsEnum.otherContributorType
            }
            submitFormOnEnterKeyPress={submitFormOnEnterKeyPress}
        />
    ));

    return (
        <AppOverflow>
            <AppGrid title="Register">
                <p>
                    Already have an account?{' '}
                    <Link
                        to={authLoginFormRoute}
                        href={authLoginFormRoute}
                        className="link-underline"
                    >
                        Log In
                    </Link>
                    .
                </p>
                <Grid container className="margin-bottom-100">
                    <Grid item xs={12} sm={8}>
                        <p>
                            Thank you for your interest in OS Hub. In order to
                            download data from, or contribute to, OS Hub please
                            first set up a free account:
                        </p>
                        {formInputs}
                        <ShowOnly when={!!(error && error.length)}>
                            <ul style={formValidationErrorMessageStyle}>
                                {error && error.length
                                    ? error.map(err => <li key={err}>{err}</li>)
                                    : null}
                            </ul>
                        </ShowOnly>
                        <Button
                            text="Register"
                            onClick={submitForm}
                            disabled={fetching}
                        />
                    </Grid>
                </Grid>
            </AppGrid>
        </AppOverflow>
    );
}

RegisterForm.defaultProps = {
    error: null,
};

RegisterForm.propTypes = {
    clearForm: func.isRequired,
    fetching: bool.isRequired,
    error: arrayOf(string),
    form: registrationFormValuesPropType.isRequired,
    inputUpdates: registrationFormInputHandlersPropType.isRequired,
    submitForm: func.isRequired,
    submitFormOnEnterKeyPress: func.isRequired,
    sessionFetching: bool.isRequired,
};

function mapStateToProps({
    auth: {
        fetching,
        error,
        session: { fetching: sessionFetching },
        signup: { form },
    },
}) {
    return {
        fetching,
        error,
        form,
        sessionFetching,
    };
}

function mapDispatchToProps(dispatch) {
    const makeInputChangeHandler = (field, getStateFromEvent) => e =>
        dispatch(
            updateSignUpFormInput({
                value: getStateFromEvent(e),
                field,
            }),
        );

    const fieldsByKey = keyBy(registrationFormFields, 'id');

    const inputUpdates = fromPairs(
        Object.values(registrationFieldsEnum).map(field => [
            field,
            makeInputChangeHandler(
                field,
                getStateFromEventForEventType[fieldsByKey[field].type],
            ),
        ]),
    );

    return {
        inputUpdates,
        submitForm: () => dispatch(submitSignUpForm()),
        clearForm: () => dispatch(resetAuthFormState()),
        submitFormOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(() =>
            dispatch(submitSignUpForm()),
        ),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(RegisterForm);
