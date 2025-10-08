import React, { useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import Routes from './Routes';
import { fetchEmbedConfig } from './actions/embeddedMap';
import {
    OARColor,
    OARSecondaryColor,
    OARActionColor,
    USER_DEFAULT_STATE,
} from './util/constants';
import EmbeddedMapUnauthorized from './components/EmbeddedMapUnauthorized';
import { useGlobalErrorHandler } from './util/hooks';
import 'typeface-darker-grotesque';

import './App.css';
import COLOURS from './util/COLOURS';
import { userPropType, reactSelectOptionPropType } from './util/propTypes';

const configOrDefault = (configColor, defaultColor) =>
    !configColor || configColor === OARColor ? defaultColor : configColor;

function App({
    embed,
    contributor,
    getEmbedConfig,
    config,
    embedError,
    embedLoading,
    user,
}) {
    const contributorId = contributor?.value;

    // Set up global error handlers to catch errors from third-party libraries.
    useGlobalErrorHandler(user);

    useEffect(() => {
        if (embed && contributorId) {
            getEmbedConfig(contributorId);
        }
    }, [embed, contributorId, getEmbedConfig]);

    const theme = useMemo(
        () =>
            createMuiTheme({
                breakpoints: {
                    values: {
                        xs: 0,
                        sm: 700,
                        md: 900,
                        lg: 1280,
                        xl: 1920,
                    },
                },
                typography: {
                    fontFamily: config.font,
                    fontWeightSemiBold: 600,
                    fontWeightSemiBoldPlus: 700,
                    fontWeightBold: 800,
                    fontWeightExtraBold: 900,
                },
                palette: {
                    primary: {
                        main: config.color || OARColor,
                        coloredBackground:
                            config.color === OARColor ? '#c7d2fa' : '',
                    },
                    secondary: {
                        main: configOrDefault(config.color, OARSecondaryColor),
                    },
                    action: {
                        main: configOrDefault(config.color, OARActionColor),
                        contrastText: 'rgba(0, 0, 0, 0.87)',
                        dark: configOrDefault(
                            config.color,
                            'rgb(178, 144, 44)',
                        ),
                        light: configOrDefault(
                            config.color,
                            'rgb(255, 216, 101)',
                        ),
                    },
                    background: {
                        grey: COLOURS.LIGHT_GREY,
                    },
                },
            }),
        [config],
    );

    if (embed && embedLoading) {
        return null;
    }

    if (embed && embedError) {
        return <EmbeddedMapUnauthorized error={embedError} />;
    }

    return (
        <MuiThemeProvider theme={theme}>
            <Routes />
        </MuiThemeProvider>
    );
}

App.defaultProps = {
    contributor: null,
    embedError: [],
    embedLoading: false,
    user: USER_DEFAULT_STATE,
};

App.propTypes = {
    embed: PropTypes.bool.isRequired,
    contributor: reactSelectOptionPropType,
    getEmbedConfig: PropTypes.func.isRequired,
    config: PropTypes.shape({
        font: PropTypes.string.isRequired,
        color: PropTypes.string,
    }).isRequired,
    embedError: PropTypes.arrayOf(PropTypes.string),
    embedLoading: PropTypes.bool,
    user: userPropType,
};

function mapStateToProps({
    embeddedMap: { embed, config, error, loading },
    filters,
    auth: {
        user: { user },
    },
}) {
    return {
        embed: !!embed,
        contributor: filters?.contributors[0],
        config,
        embedError: error,
        embedLoading: loading,
        user,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getEmbedConfig: id => dispatch(fetchEmbedConfig(id)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(App);
