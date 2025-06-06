import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { userPropType } from '../util/propTypes';
import { logErrorToRollbar } from './../util/util';
import { USER_DEFAULT_STATE } from '../util/constants';

const styles = {
    hash: {
        background: '#e6e6e6',
        padding: '20px',
        width: '100%',
        overflowWrap: 'break-word',
        margin: 'auto',
        fontSize: '12px',
        letterSpacing: '1px',
        color: '#7d7d7d',
        boxShadow: '0px 6px 20px -8px #000',
    },
    errorContainer: {
        width: '500px',
        margin: 'auto',
    },
};

class ErrorBoundary extends Component {
    state = {};

    componentDidCatch(error) {
        this.setState({ error });
        const { user } = this.props;
        logErrorToRollbar(window, error, user);
    }

    // To decode this later, just run "atob(hashedStringHere)"
    encodeErrorMessage = error =>
        btoa(`${error.message} ::::::: ${error.stack}`);

    render() {
        if (this.state.error) {
            return (
                <div style={styles.errorContainer}>
                    <h2>Whoops! Something went wrong :(</h2>
                    <p>
                        Weve recorded the issue and are working on a fix. If
                        this problem persists, contact support and send along
                        this text:
                    </p>
                    <div style={styles.hash} className="notranslate">
                        {this.encodeErrorMessage(this.state.error)}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

ErrorBoundary.propTypes = {
    children: PropTypes.node.isRequired,
    user: userPropType,
};

ErrorBoundary.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
}) {
    return { user };
}

export default connect(mapStateToProps)(ErrorBoundary);
