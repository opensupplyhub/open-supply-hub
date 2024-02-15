import React, { Component } from 'react';
import { connect } from 'react-redux';
import { arrayOf, func, string, bool } from 'prop-types';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';
import Tooltip from '@material-ui/core/Tooltip';
import { userApiInfoTooltipTitles } from '../util/constants';

import { fetchUserApiInfo } from '../actions/profile';
import { userApiInfoPropType } from '../util/propTypes';

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
        return (
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
                        primary="Renewal Period:"
                        secondary={renewalPeriod}
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
