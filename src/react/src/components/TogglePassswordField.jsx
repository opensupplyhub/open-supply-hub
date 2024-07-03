import React, { useState } from 'react';

import { func, objectOf, string } from 'prop-types';
import { connect } from 'react-redux';
import InputLabel from '@material-ui/core/InputLabel';
import InputBase from '@material-ui/core/InputBase';
import InputAdornment from '@material-ui/core/InputAdornment';
import IconButton from '@material-ui/core/IconButton';
import Visibility from '@material-ui/icons/VisibilityOutlined';
import VisibilityOff from '@material-ui/icons/VisibilityOffOutlined';
import { withStyles } from '@material-ui/core/styles';

import { updateLoginFormPassword, submitLoginForm } from '../actions/auth';
import {
    getValueFromEvent,
    makeSubmitFormOnEnterKeyPressFunction,
} from '../util/util';
import { togglePasswordFieldStyles } from '../util/styles';

const LOGIN_PASSWORD = 'LOGIN_PASSWORD';

function TogglePassswordField({
    password,
    updatePassword,
    submitFormOnEnterKeyPress,
    classes,
}) {
    const [showPassword, setShowPassword] = useState(false);

    const handleClickShowPassword = () => {
        setShowPassword(prevShowPassword => !prevShowPassword);
    };

    const handleMouseDownPassword = event => {
        event.preventDefault();
    };

    return (
        <div className="form__field">
            <InputLabel className={classes.lable} htmlFor={LOGIN_PASSWORD}>
                Password
            </InputLabel>
            <InputBase
                className={classes.wrapper}
                id={LOGIN_PASSWORD}
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={updatePassword}
                onKeyPress={submitFormOnEnterKeyPress}
                fullWidth
                classes={{
                    inputType: classes.inputType,
                    input: classes.input,
                    focused: classes.inputFocused,
                }}
                endAdornment={
                    <InputAdornment
                        position="end"
                        classes={{
                            root: classes.adornment,
                        }}
                    >
                        <IconButton
                            aria-label="toggle password visibility"
                            onClick={handleClickShowPassword}
                            onMouseDown={handleMouseDownPassword}
                            classes={{
                                root: classes.button,
                            }}
                        >
                            {showPassword ? <Visibility /> : <VisibilityOff />}
                        </IconButton>
                    </InputAdornment>
                }
            />
        </div>
    );
}

TogglePassswordField.prototypes = {
    password: string.isRequired,
    updatePassword: func.isRequired,
    submitFormOnEnterKeyPress: func.isRequired,
    classes: objectOf(string),
};

const mapStateToProps = ({ auth }) => {
    const { password } = auth.login.form;
    return {
        password,
    };
};

const mapDispatchToProps = dispatch => ({
    updatePassword: e =>
        dispatch(updateLoginFormPassword(getValueFromEvent(e))),
    submitFormOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(() =>
        dispatch(submitLoginForm()),
    ),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(togglePasswordFieldStyles)(TogglePassswordField));
