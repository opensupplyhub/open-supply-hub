import React from 'react';
import { string } from 'prop-types';
import COLOURS from '../../util/COLOURS';

const styles = {
    label: {
        color: COLOURS.DARK_SLATE_GREY,
        fontWeight: 600,
    },
};

const PartnerFieldLabel = ({ title }) => (
    <span style={styles.label}>{`${title}: `}</span>
);

PartnerFieldLabel.propTypes = {
    title: string.isRequired,
};

export default PartnerFieldLabel;
