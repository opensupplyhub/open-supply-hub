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
import {
    userApiInfoTooltipTitles,
    IS_NOT_SET,
    FORBIDDEN,
} from '../util/constants';

import { fetchUserApiInfo } from '../actions/profile';
import { userApiInfoPropType } from '../util/propTypes';

const styles = Object.freeze({
    errorMessagesStyles: Object.freeze({
        color: 'red',
        padding: '1rem',
    }),
});
class UserAPIInfo extends Component {
    componentDidMount() {
        return this.props.getUserApiInfo();
    }

    render() {
        const { error, userApiInfo, fetching } = this.props;
        console.log('!!! userApiInfo props', userApiInfo);

        if (error) {
            window.console.warn(error);
        }
        const {
            apiCallAllowance,
            currentCallCount,
            renewalPeriod,
        } = userApiInfo[0];
        return apiCallAllowance === FORBIDDEN ? (
            <div style={styles.errorMessagesStyles}>{FORBIDDEN}</div>
        ) : (
            <List disabled={fetching}>
                <ListItem>
                    <Tooltip
                        title={userApiInfoTooltipTitles.apiCallAllowance}
                        placement="right"
                    >
                        <IconButton aria-label="Call Limit">
                            <InfoIcon />
                        </IconButton>
                    </Tooltip>

                    <ListItemText
                        primary="Call Limit:"
                        secondary={apiCallAllowance}
                    />
                </ListItem>
                <ListItem>
                    <Tooltip
                        title={userApiInfoTooltipTitles.currentCallCount}
                        placement="right"
                    >
                        <IconButton aria-label="Current Usage">
                            <InfoIcon />
                        </IconButton>
                    </Tooltip>

                    <ListItemText
                        primary="Current Usage:"
                        secondary={currentCallCount}
                    />
                </ListItem>
                <ListItem>
                    <Tooltip
                        title={userApiInfoTooltipTitles.renewalPeriod}
                        placement="right"
                    >
                        <IconButton aria-label="Renewal Period">
                            <InfoIcon />
                        </IconButton>
                    </Tooltip>

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
                        // const element = <h1 style={{ color: 'red' }}>Hello world</h1>
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
