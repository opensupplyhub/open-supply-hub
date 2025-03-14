import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, func, string, bool } from 'prop-types';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import InfoIcon from '@material-ui/icons/Info';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';

import { userApiInfoTooltipTitles, IS_NOT_SET } from '../util/constants';

import { fetchUserApiInfo } from '../actions/profile';
import { userApiInfoPropType } from '../util/propTypes';
import StyledTooltip from './StyledTooltip';

const componentStyles = Object.freeze({
    withoutMargin: Object.freeze({
        marginBlockStart: '0',
        marginBlockEnd: '0',
    }),
});

const UserAPIInfo = ({ error, data, fetching, getUserApiInfo }) => {
    useEffect(() => {
        getUserApiInfo();
    }, []);

    if (fetching) {
        return <CircularProgress />;
    }

    if (error) {
        return (
            <Typography variant="body2" style={{ color: 'red' }}>
                {error}
            </Typography>
        );
    }

    return (
        <List>
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
                        data.apiCallAllowance === IS_NOT_SET ? (
                            <Typography
                                variant="body2"
                                style={{ color: 'red' }}
                            >
                                {data.apiCallAllowance}
                            </Typography>
                        ) : (
                            data.apiCallAllowance
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
                    secondary={data.currentCallCount}
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
                        data.renewalPeriod === IS_NOT_SET ? (
                            <Typography
                                variant="body2"
                                style={{ color: 'red' }}
                            >
                                {data.renewalPeriod}
                            </Typography>
                        ) : (
                            <p style={componentStyles.withoutMargin}>
                                {data.renewalPeriod}
                            </p>
                        )
                    }
                />
            </ListItem>
        </List>
    );
};

UserAPIInfo.defaultProps = {
    error: null,
};

UserAPIInfo.propTypes = {
    error: arrayOf(string),
    data: userApiInfoPropType.isRequired,
    getUserApiInfo: func.isRequired,
    fetching: bool.isRequired,
};

function mapStateToProps({
    profile: {
        userApiInfo: { data, error, fetching },
    },
}) {
    return {
        data,
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
