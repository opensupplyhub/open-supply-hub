import React from 'react';
import Grid from '@material-ui/core/Grid';
import PropTypes from 'prop-types';

import { OARFont } from '../util/constants';

export default function AppGrid({
    style,
    title,
    children,
    backButtonComponent,
}) {
    return (
        <Grid container>
            <Grid
                item
                xs={12}
                sm={9}
                style={{
                    marginLeft: 'auto',
                    marginRight: 'auto',
                }}
            >
                <Grid container style={style}>
                    <Grid item xs={12}>
                        <h2
                            style={{
                                fontFamily: OARFont,
                                fontWeight: 'normal',
                                fontSize: '32px',
                            }}
                        >
                            {backButtonComponent} {title}
                        </h2>
                    </Grid>
                    {children}
                </Grid>
            </Grid>
        </Grid>
    );
}

AppGrid.defaultProps = {
    style: {},
    backButtonComponent: null,
};

AppGrid.propTypes = {
    title: PropTypes.node.isRequired,
    style: PropTypes.object, // eslint-disable-line react/forbid-prop-types
    children: PropTypes.node.isRequired,
    backButtonComponent: PropTypes.node,
};
