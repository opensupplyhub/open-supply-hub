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

import { togglePasswordFieldStyles } from '../util/styles';

function TogglePassswordField({
    id,
    value,
    label,
    updatePassword,
    submitFormOnEnterKeyPress,
    classes,
    children,
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
            <InputLabel className={classes.lable} htmlFor={id}>
                {label}
                {children || null}
            </InputLabel>
            <InputBase
                className={classes.wrapper}
                id={id}
                type={showPassword ? 'text' : 'password'}
                value={value}
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
    id: string.isRequired,
    value: string.isRequired,
    label: string.isRequired,
    updatePassword: func.isRequired,
    submitFormOnEnterKeyPress: func.isRequired,
    classes: objectOf(string),
};

export default connect()(
    withStyles(togglePasswordFieldStyles)(TogglePassswordField),
);
