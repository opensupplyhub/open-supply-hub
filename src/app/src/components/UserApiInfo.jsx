import React, { Component } from 'react';
import { connect } from 'react-redux';
import { arrayOf, func, string, bool } from 'prop-types';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import {
    userApiInfoTooltipTitles,
    IS_NOT_SET,
    FORBIDDEN,
} from '../util/constants';

import { fetchUserApiInfo } from '../actions/profile';
import { userApiInfoPropType } from '../util/propTypes';

const StyledTooltip = withStyles({
    tooltip: {
        color: 'rgba(0, 0, 0, 0.8)',
        fontSize: '0.875rem',
        backgroundColor: 'white',
        border: 'solid rgba(0, 0, 0, 0.25)',
        borderRadius: '10px',
        padding: '10px',
        lineHeight: '1',
    },
})(Tooltip);

class UserAPIInfo extends Component {
    componentDidMount() {
        return this.props.getUserApiInfo();
    }

    render() {
        const { error, userApiInfo, fetching } = this.props;

        if (error) {
            window.console.warn(error);
        }

        const {
            apiCallAllowance,
            currentCallCount,
            renewalPeriod,
        } = userApiInfo[0];

        return (
            <List disabled={fetching}>
                <ListItem>
                    <StyledTooltip
                        title={userApiInfoTooltipTitles.apiCallAllowance}
                        placement="right"
                    >
                        <IconButton aria-label="Call Limit">
                            <InfoIcon />
                        </IconButton>
                    </StyledTooltip>

                    <ListItemText
                        primary="Call Limit:"
                        secondary={
                            apiCallAllowance === FORBIDDEN ? (
                                <Typography
                                    variant="body2"
                                    style={{ color: 'red' }}
                                >
                                    {apiCallAllowance}
                                </Typography>
                            ) : (
                                apiCallAllowance
                            )
                        }
                    />
                </ListItem>
                <ListItem>
                    <StyledTooltip
                        title={userApiInfoTooltipTitles.currentCallCount}
                        placement="right"
                    >
                        <IconButton aria-label="Current Usage">
                            <InfoIcon />
                        </IconButton>
                    </StyledTooltip>

                    <ListItemText
                        primary="Current Usage:"
                        secondary={currentCallCount}
                    />
                </ListItem>
                <ListItem>
                    <StyledTooltip
                        title={userApiInfoTooltipTitles.renewalPeriod}
                        placement="right"
                    >
                        <IconButton aria-label="Renewal Period">
                            <InfoIcon />
                        </IconButton>
                    </StyledTooltip>

                    <ListItemText
                        disableTypography
                        primary="Renewal Period:"
                        secondary={
                            renewalPeriod === IS_NOT_SET ? (
                                <Typography
                                    variant="body2"
                                    style={{ color: 'red' }}
                                >
                                    {renewalPeriod}
                                </Typography>
                            ) : (
                                renewalPeriod
                            )
                        }
                    />
                </ListItem>
            </List>
        );
    }
}

UserAPIInfo.defaultProps = {
    error: null,
};

UserAPIInfo.propTypes = {
    error: arrayOf(string),
    userApiInfo: arrayOf(userApiInfoPropType).isRequired,
    getUserApiInfo: func.isRequired,
    fetching: bool.isRequired,
};

function mapStateToProps({
    profile: {
        userApiInfo: { userApiInfo, error, fetching },
    },
}) {
    return {
        userApiInfo,
        error,
        fetching,
    };
}

function mapDispatchToProps(dispatch, { uid }) {
    return {
        getUserApiInfo: () => dispatch(fetchUserApiInfo(uid)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(UserAPIInfo);
