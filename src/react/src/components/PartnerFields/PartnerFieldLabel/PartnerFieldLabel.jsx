import React from 'react';
import { string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import partnerFieldLabelStyles from './styles';

const PartnerFieldLabel = ({ title, classes }) => (
    <span className={classes.label}>{`${title}: `}</span>
);

PartnerFieldLabel.propTypes = {
    title: string.isRequired,
};

export default withStyles(partnerFieldLabelStyles)(PartnerFieldLabel);
