import React, { useEffect, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import Radio from '@material-ui/core/Radio';

import { connect } from 'react-redux';
import { func } from 'prop-types';
import BadgeClaimed from './BadgeClaimed';
import { updateClaimFacilityIntro } from '../actions/claimFacility';

const radioGroupStyles = Object.freeze({
    radioItem: {
        marginRight: '30px',
    },
    radio: {
        color: 'rgb(0, 0, 0)',
        padding: '3px 5px 0 7px',
    },
});

const inputGroupStyles = Object.freeze({
    width: '100%',
    paddingTop: '30px',
});

const boldStyle = Object.freeze({
    fontWeight: 'bold',
});
const paragraphStyle = Object.freeze({
    paddingBottom: '20px',
});
const listStyle = Object.freeze({
    margin: '0',
});
const inlineStyle = Object.freeze({
    display: 'inline-block',
});

function ClaimFacilityIntroStep({ agreement, updateAgreement }) {
    console.log('1 toString(agreement)', agreement);

    const [selectedValue, setRadio] = useState('');

    const handleChange = event => {
        setRadio(event.target.value);
    };

    useEffect(() => {
        updateAgreement(selectedValue === 'true');
    }, [selectedValue]);

    return (
        <div style={inputGroupStyles}>
            <div style={paragraphStyle}>
                <Typography variant="heading" style={boldStyle}>
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
                    <BadgeClaimed fontSize="18px" />
                    displayed next to it on the OS Hub profile.
                </Typography>
            </div>
            <div style={paragraphStyle}>
                <Typography variant="heading" style={boldStyle}>
                    To complete a claim request, you will need to submit the
                    following documentation:
                </Typography>
                <Typography variant="subheading">
                    <ul style={listStyle}>
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
            <div style={paragraphStyle}>
                <Typography
                    variant="heading"
                    style={{ ...boldStyle, ...inlineStyle }}
                >
                    Note:
                </Typography>
                &nbsp;
                <Typography variant="subheading" style={inlineStyle}>
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
                        value="true"
                        control={<Radio style={radioGroupStyles.radio} />}
                        label={
                            <Typography variant="subheading">
                                Yes, I am an owner or senior manager at this
                                production location and would like to submit a
                                claim request.
                            </Typography>
                        }
                        style={radioGroupStyles.radioItem}
                    />
                    <FormControlLabel
                        value="false"
                        control={<Radio style={radioGroupStyles.radio} />}
                        label={
                            <Typography variant="subheading">
                                No, I do not want to submit a claim request.
                            </Typography>
                        }
                        style={radioGroupStyles.radioItem}
                    />
                </RadioGroup>
            </FormControl>
        </div>
    );
}

ClaimFacilityIntroStep.propTypes = {
    agreement: Boolean.isRequired,
    updateAgreement: func.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: {
            formData: { agreement },
        },
    },
}) {
    return {
        agreement,
    };
}

const mapDispatchToProps = dispatch => ({
    updateAgreement: selectedValue => {
        dispatch(updateClaimFacilityIntro(selectedValue));
    },
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimFacilityIntroStep);
