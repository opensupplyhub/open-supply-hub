import React from 'react';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';

import MenuList from '@material-ui/core/MenuList';
import MenuItem from '@material-ui/core/MenuItem';
import Typography from '@material-ui/core/Typography';

import { facilityDetailsActions } from '../../../util/constants';

import {
    makeContributeProductionLocationUpdateURL,
    makeReportADuplicateEmailLink,
    makeDisputeClaimEmailLink,
} from '../../../util/util';

const contributeFieldsStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
    });

const ProductionLocationDetailsContributeFields = ({ classes, osId }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Contribute to this profile
        </Typography>
        <MenuList>
            <MenuItem>
                <Link
                    href={makeReportADuplicateEmailLink(osId)}
                    target="_blank"
                    rel="noreferrer"
                >
                    {facilityDetailsActions.REPORT_AS_DUPLICATE}
                </Link>
            </MenuItem>
            <MenuItem>
                <Link
                    href={makeContributeProductionLocationUpdateURL(osId)}
                    target="_blank"
                    rel="noreferrer"
                >
                    {facilityDetailsActions.SUGGEST_AN_EDIT}
                </Link>
            </MenuItem>
            <MenuItem>
                <Link
                    href={makeDisputeClaimEmailLink(osId)}
                    target="_blank"
                    rel="noreferrer"
                >
                    {facilityDetailsActions.DISPUTE_CLAIM}
                </Link>
            </MenuItem>
        </MenuList>
    </div>
);

export default withStyles(contributeFieldsStyles)(
    ProductionLocationDetailsContributeFields,
);
