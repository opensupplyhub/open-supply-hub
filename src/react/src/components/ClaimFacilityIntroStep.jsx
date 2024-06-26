import React, { useEffect, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import Radio from '@material-ui/core/Radio';

import { connect } from 'react-redux';
import { func } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import BadgeClaimed from './BadgeClaimed';
import { updateClaimFacilityIntro } from '../actions/claimFacility';

const styles = theme =>
    Object.freeze({
        rightMargin: {
            marginRight: theme.spacing.unit * 4,
        },
        radioStyle: {
            color: 'rgb(0, 0, 0) !important',
            padding: '3px 5px 0 7px',
        },
        inputGroup: {
            width: '100%',
            paddingTop: theme.spacing.unit * 4,
        },
        bold: {
            fontWeight: 'bold',
        },
        paragraphStyle: {
            paddingBottom: theme.spacing.unit * 3,
        },
        listStyle: {
            margin: '0',
        },
        inlineStyle: {
            display: 'inline',
        },
    });

function ClaimFacilityIntroStep({ classes, updateAgreement }) {
    const [selectedValue, setRadio] = useState('no');

    const handleChange = event => {
        setRadio(event.target.value);
    };

    useEffect(() => {
        updateAgreement(selectedValue);
    }, [selectedValue]);

    return (
        <div className={classes.inputGroup}>
            <div className={classes.paragraphStyle}>
                <Typography variant="subheading" className={classes.bold}>
                    What is a claim?
                </Typography>
                <Typography variant="subheading">
                    Owners and senior managers can claim their production
                    locations on OS Hub by submitting information that allows
                    the OS Hub team to confirm the production location’s name
                    and address AND that the person claiming the production
                    location is affiliated with it. Once a claim is approved,
                    additional details can be displayed on the production
                    location’s OS Hub profile. All data contributed by a
                    claimant will have the “claimed” icon{' '}
                    <BadgeClaimed
                        fontSize="18px"
                        viewBox="0 -5 16 20"
                        overflow="visible"
                    />{' '}
                    displayed next to it on the OS Hub profile.
                </Typography>
            </div>
            <div className={classes.paragraphStyle}>
                <Typography variant="subheading" className={classes.bold}>
                    To complete a claim request, you will need to submit the
                    following documentation:
                </Typography>
                <Typography variant="subheading">
                    <ul className={classes.listStyle}>
                        <li>
                            A document or website that lists the name and
                            address of the production location (e.g. utility
                            bill, business website, registration document, or
                            LinkedIn profile)
                        </li>
                        <li>
                            A document or website that shows your role at the
                            production location (e.g. business website,
                            employment badge, letter of employment, or other
                            relevant employment documentation){' '}
                        </li>
                    </ul>
                </Typography>
            </div>
            <div className={classes.paragraphStyle}>
                <b>Note:</b>
                &nbsp;
                <Typography
                    variant="subheading"
                    className={classes.inlineStyle}
                >
                    Any documentation appearing to be forged or counterfeit may
                    result in your claim request being denied.
                </Typography>
            </div>
            <FormControl>
                <RadioGroup
                    aria-labelledby="demo-controlled-radio-buttons-group"
                    name="controlled-radio-buttons-group"
                    value={selectedValue}
                    onChange={handleChange}
                >
                    <FormControlLabel
                        value="yes"
                        control={<Radio className={classes.radioStyle} />}
                        label={
                            <Typography variant="subheading">
                                Yes, I am an owner or senior manager at this
                                production location and would like to submit a
                                claim request.
                            </Typography>
                        }
                        className={classes.rightMargin}
                    />
                    <FormControlLabel
                        value="no"
                        control={<Radio className={classes.radioStyle} />}
                        label={
                            <Typography variant="subheading">
                                No, I do not want to submit a claim request.
                            </Typography>
                        }
                        className={classes.rightMargin}
                    />
                </RadioGroup>
            </FormControl>
        </div>
    );
}

ClaimFacilityIntroStep.propTypes = {
    updateAgreement: func.isRequired,
};

const mapStateToProps = ({
    claimFacility: {
        claimData: {
            formData: { agreement },
        },
    },
}) => ({
    agreement,
});

const mapDispatchToProps = dispatch => ({
    updateAgreement: selectedValue => {
        dispatch(updateClaimFacilityIntro(selectedValue));
    },
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withTheme()(withStyles(styles)(ClaimFacilityIntroStep)));
