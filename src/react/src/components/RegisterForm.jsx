import React, { Component } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import memoize from 'lodash/memoize';

import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import ShowOnly from './ShowOnly';
import Button from './Button';
import RegisterFormField from './RegisterFormField';

import {
    updateSignUpFormInput,
    submitSignUpForm,
    resetAuthFormState,
} from '../actions/auth';

import {
    OTHER,
    registrationFieldsEnum,
    registrationFormFields,
    authLoginFormRoute,
} from '../util/constants';

import {
    registrationFormValuesPropType,
    registrationFormInputHandlersPropType,
} from '../util/propTypes';

import {
    getStateFromEventForEventType,
    makeSubmitFormOnEnterKeyPressFunction,
} from '../util/util';

import { formValidationErrorMessageStyle } from '../util/styles';

class RegisterForm extends Component {
    state = {
        formSubmitted: false,
    };

    componentDidUpdate({ fetching: wasFetching }) {
        const { fetching, error } = this.props;

        if (error) {
            return null;
        }

        if (fetching) {
            return null;
        }

        if (!wasFetching) {
            return null;
        }

        return this.setFormSubmitted();
    }

    componentWillUnmount() {
        return this.props.clearForm();
    }

    setFormSubmitted = () =>
        this.setState(state =>
            Object.assign({}, state, {
                formSubmitted: true,
            }),
        );

    render() {
        const {
            fetching,
            error,
            form,
            inputUpdates,
            submitForm,
            submitFormOnEnterKeyPress,
            sessionFetching,
        } = this.props;

        if (sessionFetching) {
            return null;
        }

        if (this.state.formSubmitted) {
            return (
                <AppOverflow>
                    <AppGrid title="Registration was successful!">
                        <p>
                            Check your email for instructions about how to
                            verify your account.
                        </p>
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
                                Thank you for your interest in OS Hub. In order
                                to download data from, or contribute to, OS Hub
                                please first set up a free account:
                            </p>
                            {formInputs}
                            <ShowOnly when={!!(error && error.length)}>
                                <ul style={formValidationErrorMessageStyle}>
                                    {error && error.length
                                        ? error.map(err => (
                                              <li key={err}>{err}</li>
                                          ))
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

const mapDispatchToProps = memoize(dispatch => {
    const makeInputChangeHandler = (field, getStateFromEvent) => e =>
        dispatch(
            updateSignUpFormInput({
                value: getStateFromEvent(e),
                field,
            }),
        );

    const inputUpdates = Object.values(registrationFieldsEnum).reduce(
        (acc, field) => {
            const { type } = registrationFormFields.find(
                ({ id }) => id === field,
            );
            const getStateFromEvent = getStateFromEventForEventType[type];

            return Object.assign({}, acc, {
                [field]: makeInputChangeHandler(field, getStateFromEvent),
            });
        },
        {},
    );

    return {
        inputUpdates,
        submitForm: () => dispatch(submitSignUpForm()),
        clearForm: () => dispatch(resetAuthFormState()),
        submitFormOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(() =>
            dispatch(submitSignUpForm()),
        ),
    };
});

export default connect(mapStateToProps, mapDispatchToProps)(RegisterForm);
