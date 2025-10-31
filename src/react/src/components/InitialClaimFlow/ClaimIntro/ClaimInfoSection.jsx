import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import InfoIcon from '@material-ui/icons/Info';
import StarIcon from '@material-ui/icons/Star';
import COLOURS from '../../../util/COLOURS';
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
                1. Confirm Your Eligibility
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography variant="body2" className={classes.boxText}>
                        Claim requests must be submitted by a current employee
                        of the location or its parent company.
                    </Typography>
                </li>
                <li>
                    <Typography variant="body2" className={classes.boxText}>
                        If you&apos;re not an owner or manager, you can still
                        proceed by providing your supervisor&apos;s contact
                        information for verification.
                    </Typography>
                </li>
            </ul>
        </div>
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                2. Prove Your Name and Role
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>OPTIONS:</strong> Company website showing your name and
                role, Employee ID badge, Employment letter, Job contract, Link
                to your LinkedIn profile, Business card, Audit reports.
            </Typography>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={employeeIdExample}
                    alt="Example employee ID badge"
                    label="Employee ID Badge"
                />
                <ExampleImage
                    src={employmentLetterExample}
                    alt="Example employment letter"
                    label="Employment Letter"
                />
                <ExampleImage
                    src={businessCardExample}
                    alt="Example business card"
                    label="Business Card"
                />
            </div>
        </div>

        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                3. Prove Your Company Name and Address
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>OPTIONS:</strong> Business registration, Business
                license, Utility bill, link to company website, link to company
                LinkedIn page.
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>NOTE:</strong> The document must show the same company
                name and address as listed on your OS Hub profile.
            </Typography>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={businessRegistrationExample}
                    alt="Example business registration certificate"
                    label="Business Registration"
                />
                <ExampleImage
                    src={businessLicenseExample}
                    alt="Example business license"
                    label="Business License"
                />
                <ExampleImage
                    src={utilityBillExample}
                    alt="Example utility bill"
                    label="Utility Bill"
                />
            </div>
        </div>
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                4. Add Key Details
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide information about the production location such as
                Certifications, Number of Workers, Contact Information, and
                more.
            </Typography>
        </div>

        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                5. Get a Credible and Confirmed Profile
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
                    Learn more about claiming your production location
                </a>
            </Typography>
        </div>
        <div className={classes.boxContainer}>
            <Typography variant="body2" className={classes.boxDescription}>
                <InfoIcon className={classes.warningIcon} />
                <strong className={classes.warningBoldText}>
                    IMPORTANT!
                </strong>{' '}
                Any documentation appearing to be forged or counterfeit may
                result in your claim request being denied.
            </Typography>
        </div>

        <div className={`${classes.stepBox} ${classes.blueStep}`}>
            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.blueNumber}`}>
                    1
                </div>
                <div>
                    <Typography
                        variant="title"
                        style={{ color: COLOURS.DARK_BLUE }}
                    >
                        Confirm Your Eligibility
                    </Typography>
                    <div>
                        <div className={classes.step}>
                            <div className={classes.stepNumber}>1</div>
                            <Typography
                                variant="title"
                                className={classes.stepTitle}
                                style={{ color: COLOURS.DARK_BLUE }}
                            >
                                Confirm Your Eligibility
                            </Typography>
                        </div>
                        <div className={classes.bulletPoint}>
                            <span
                                className={`${classes.bullet} ${classes.blueBullet}`}
                            />
                            <Typography
                                variant="body2"
                                className={classes.stepText}
                                style={{ color: COLOURS.LIGHT_MATERIAL_BLUE }}
                            >
                                Claim requests must be submitted by a current
                                employee of the location or its parent company.
                            </Typography>
                        </div>
                        <div className={classes.bulletPoint}>
                            <span
                                className={`${classes.bullet} ${classes.blueBullet}`}
                            />
                            <Typography
                                variant="body2"
                                className={classes.stepText}
                                style={{ color: COLOURS.LIGHT_MATERIAL_BLUE }}
                            >
                                If you&apos;re not an owner or manager, you can
                                still proceed by providing your
                                supervisor&apos;s contact information for
                                verification.
                            </Typography>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div className={classes.twoColumnGrid}>
            <div className={`${classes.stepBox} ${classes.purpleStep}`}>
                <div className={classes.stepHeader}>
                    <div
                        className={`${classes.stepNumber} ${classes.purpleNumber}`}
                    >
                        2
                    </div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: COLOURS.DARK_PURPLE }}
                    >
                        Prove Your Name and Role
                    </Typography>
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: COLOURS.PURPLE_TEXT, marginBottom: 16 }}
                >
                    <strong>OPTIONS:</strong> Company website showing your name
                    and role, Employee ID badge, Employment letter, Job
                    contract, Link to your LinkedIn profile, Business card,
                    Audit reports.
                </Typography>
                <div className={classes.examplesContainer}>
                    <ExampleImage
                        src={employeeIdExample}
                        alt="Example employee ID badge"
                        label="Employee ID Badge"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                    />
                    <ExampleImage
                        src={employmentLetterExample}
                        alt="Example employment letter"
                        label="Employment Letter"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                    />
                    <ExampleImage
                        src={businessCardExample}
                        alt="Example business card"
                        label="Business Card"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                    />
                </div>
            </div>
            <div className={`${classes.stepBox} ${classes.greenStep}`}>
                <div className={classes.stepHeader}>
                    <div
                        className={`${classes.stepNumber} ${classes.greenNumber}`}
                    >
                        3
                    </div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: COLOURS.DARK_MATERIAL_GREEN }}
                    >
                        Prove Your Company Name and Address
                    </Typography>
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: COLOURS.GREEN_TEXT, marginBottom: 8 }}
                >
                    <strong>OPTIONS:</strong> Business registration, Business
                    license, Utility bill, link to company website, link to
                    company LinkedIn page.
                </Typography>
                <div className={classes.noteBox}>
                    <Typography
                        variant="body2"
                        className={classes.stepText}
                        style={{ color: COLOURS.GREEN_TEXT }}
                    >
                        <strong>NOTE:</strong> The document must show the same
                        company name and address as listed on your OS Hub
                        profile.
                    </Typography>
                </div>
                <div className={classes.examplesContainer}>
                    <ExampleImage
                        src={businessRegistrationExample}
                        alt="Example business registration certificate"
                        label="Business Registration"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                    />
                    <ExampleImage
                        src={businessLicenseExample}
                        alt="Example business license"
                        label="Business License"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                    />
                    <ExampleImage
                        src={utilityBillExample}
                        alt="Example utility bill"
                        label="Utility Bill"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                    />
                </div>
            </div>
        </div>
        <div className={`${classes.stepBox} ${classes.amberStep}`}>
            <div style={{ textAlign: 'center' }}>
                <span className={classes.maxValueBadge}>
                    <StarIcon style={{ fontSize: 16, marginRight: 4 }} />
                    Maximum Value
                </span>
            </div>

            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.amberNumber}`}>
                    4
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: COLOURS.DEEP_ORANGE }}
                >
                    <strong style={{ fontSize: 20 }}>Add Key Details:</strong>{' '}
                    Provide information about the production location such as
                    Certifications, Number of Workers, Contact Information, and
                    more.
                </Typography>
            </div>

            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.amberNumber}`}>
                    5
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: COLOURS.DEEP_ORANGE }}
                >
                    <strong style={{ fontSize: 20 }}>
                        Get a Credible and Confirmed Profile:
                    </strong>{' '}
                    After the claim is approved, you get a credible and
                    confirmed profile—with a green banner and Claimed badge—that
                    helps buyers trust and find your company.{' '}
                    <a
                        href={ClaimFacilityInfoLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={classes.link}
                    >
                        Learn more about claiming your production location
                    </a>
                </Typography>
            </div>
        </div>
        <div className={classes.warningBox}>
            <InfoIcon className={classes.warningIcon} />
            <Typography variant="subheading" style={{ fontSize: 16 }}>
                <strong style={{ color: COLOURS.MATERIAL_RED, fontSize: 16 }}>
                    IMPORTANT!
                </strong>{' '}
                Any documentation appearing to be forged or counterfeit may
                result in your claim request being denied.
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
