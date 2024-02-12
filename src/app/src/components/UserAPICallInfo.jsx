import React, { Component } from 'react';
import { connect } from 'react-redux';
import { arrayOf, func, string, bool } from 'prop-types';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';

import { fetchAPICallInfo } from '../actions/profile';

class UserAPICallInfo extends Component {
    componentDidMount() {
        return this.props.getAPICallInfo();
    }

    render() {
        const { error, apiCallInfo, fetching } = this.props;

        if (error) {
            window.console.warn(error);
        }
        return apiCallInfo ? (
            <List disabled={fetching}>
                <ListItem>
                    <IconButton aria-label="Info" onClick={() => {}}>
                        <InfoIcon />
                    </IconButton>

                    <ListItemText
                        primary="Call Limit:"
                        secondary={apiCallInfo.apiCallAllowance}
                    />
                </ListItem>
                <ListItem>
                    <IconButton aria-label="Info" onClick={() => {}}>
                        <InfoIcon />
                    </IconButton>

                    <ListItemText
                        primary="Current Usage:"
                        secondary={apiCallInfo.currentCallCount}
                    />
                </ListItem>
                <ListItem>
                    <IconButton aria-label="Info" onClick={() => {}}>
                        <InfoIcon />
                    </IconButton>

                    <ListItemText
                        primary="Renewal Period:"
                        secondary={apiCallInfo.renewalPeriod}
                    />
                </ListItem>
            </List>
        ) : (
            <>Error</>
        );
    }
}

UserAPICallInfo.defaultProps = {
    error: null,
    apiCallAllowance: '0',
    currentCallCount: '0',
    renewalPeriod: '',
};

UserAPICallInfo.propTypes = {
    error: arrayOf(string),
    apiCallAllowance: string,
    currentCallCount: string,
    renewalPeriod: string,
    getAPICallInfo: func.isRequired,
    fetching: bool.isRequired,
};

function mapStateToProps({
    profile: {
        apiCallInfo: {
            apiCallAllowance,
            currentCallCount,
            renewalPeriod,
            error,
            fetching,
        },
    },
}) {
    return {
        apiCallAllowance,
        currentCallCount,
        renewalPeriod,
        error,
        fetching,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getAPICallInfo: () => dispatch(fetchAPICallInfo()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(UserAPICallInfo);
