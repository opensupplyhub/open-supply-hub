import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import InfoIcon from '@material-ui/icons/Info';
import DialogTooltip from '../../Contribute/DialogTooltip';
import { ClaimFacilityInfoLink } from '../../../util/constants';
import { claimInfoStyles } from './styles';
import ExampleImage from './ExampleImage';

import businessRegistrationExample from '../../../images/business-registration-example.jpg';
import businessLicenseExample from '../../../images/business-license-example.jpg';
import utilityBillExample from '../../../images/utility-bill-example.jpg';
import employeeIdExample from '../../../images/employee-id-example.jpg';
import employmentLetterExample from '../../../images/employment-letter-example.jpg';
import businessCardExample from '../../../images/business-card-example.jpg';

const ClaimInfoSection = ({ classes, children }) => (
    <div className={classes.root}>
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={`${classes.stepNumber} ${classes.blueStep}`}>
                    1
                </span>
                <span className={classes.stepTitle}>
                    Confirm Your Eligibility
                </span>
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Confirm that you are eligible to claim this production location,
                keeping in mind:
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Claim requests must be submitted by a current employee
                        of the location or its parent company
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        If you&apos;re not an owner or manager, you can still
                        proceed by providing your supervisor&apos;s contact
                        information for verification
                    </Typography>
                </li>
            </ul>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={`${classes.stepNumber} ${classes.purpleStep}`}>
                    2
                </span>
                <span className={classes.stepTitle}>
                    Prove Your Name and Role
                </span>
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide the document about your name and role,{' '}
                <strong>OPTIONS:</strong>
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Company website showing your name and role
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Employee ID badge or employment letter
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Job contract or business card
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Link to your LinkedIn profile
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Audit reports
                    </Typography>
                </li>
            </ul>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={employeeIdExample}
                    alt="Example employee ID badge"
                    label="Employee ID Badge"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
                <ExampleImage
                    src={employmentLetterExample}
                    alt="Example employment letter"
                    label="Employment Letter"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
                <ExampleImage
                    src={businessCardExample}
                    alt="Example business card"
                    label="Business Card"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
            </div>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={`${classes.stepNumber} ${classes.greenStep}`}>
                    3
                </span>
                <span className={classes.stepTitle}>
                    Prove Your Company Name and Address
                </span>
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide the document about your company name and address,{' '}
                <strong>OPTIONS:</strong>
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Business registration or business license
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Utility bill
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Link to company website or LinkedIn page
                    </Typography>
                </li>
            </ul>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>NOTE:</strong> The document must show the same company
                name and address as listed on your OS Hub profile.
            </Typography>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={businessRegistrationExample}
                    alt="Example business registration certificate"
                    label="Business Registration"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
                <ExampleImage
                    src={businessLicenseExample}
                    alt="Example business license"
                    label="Business License"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
                <ExampleImage
                    src={utilityBillExample}
                    alt="Example utility bill"
                    label="Utility Bill"
                    labelColorClass="defaultLabel"
                    borderClass="noBorder"
                />
            </div>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={`${classes.stepNumber} ${classes.amberStep}`}>
                    4
                </span>
                <span className={classes.stepTitle}>Add Key Details</span>
                <DialogTooltip
                    text="For maximum value, add key details to your production location to help others find you online."
                    childComponent={
                        <span className={classes.maxValueBadge}>★</span>
                    }
                />
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide information about the production location, such as:
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Certifications
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Number of Workers
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Contact Information and more.
                    </Typography>
                </li>
            </ul>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={`${classes.stepNumber} ${classes.amberStep}`}>
                    5
                </span>
                <span className={classes.stepTitle}>
                    Get a Credible and Confirmed Profile
                </span>
                <DialogTooltip
                    text="After the claim is approved, you get a credible and confirmed profile—with a green banner and Claimed badge—that helps others trust and find your company."
                    childComponent={
                        <span className={classes.maxValueBadge}>★</span>
                    }
                />
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                After the claim is approved, you get a credible and confirmed
                profile—with a green banner and Claimed badge—that helps buyers
                trust and find your company.{' '}
                <a
                    href={ClaimFacilityInfoLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.link}
                >
                    Learn more about claiming your production location.
                </a>
            </Typography>
        </div>
        <div
            className={`${classes.boxContainer} ${classes.boxWarningContainer}`}
        >
            <Typography variant="body2" className={classes.boxWarningText}>
                <span className={classes.boxWarningTextIcon}>
                    <InfoIcon className={classes.warningIcon} />
                    <strong>IMPORTANT!</strong>
                </span>
                <span>
                    &nbsp;Any documentation appearing to be forged or
                    counterfeit may result in your claim request being denied.
                </span>
            </Typography>
        </div>
        <div>{children}</div>
    </div>
);

ClaimInfoSection.propTypes = {
    classes: PropTypes.object.isRequired,
    children: PropTypes.node.isRequired,
};

export default withStyles(claimInfoStyles)(ClaimInfoSection);
