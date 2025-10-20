import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import InfoIcon from '@material-ui/icons/Info';
import StarIcon from '@material-ui/icons/Star';
import COLOURS from '../../util/COLOURS';
import { ClaimFacilityInfoLink } from '../../util/constants';

import businessRegistrationExample from '../../images/business-registration-example.jpg';
import businessLicenseExample from '../../images/business-license-example.jpg';
import utilityBillExample from '../../images/utility-bill-example.jpg';
import employeeIdExample from '../../images/employee-id-example.jpg';
import employmentLetterExample from '../../images/employment-letter-example.jpg';
import businessCardExample from '../../images/business-card-example.jpg';

const claimInfoStyles = theme => ({
    root: {
        backgroundColor: COLOURS.WHITE,
        border: `1px solid ${COLOURS.BORDER_GREY}`,
        borderRadius: theme.spacing.unit,
        padding: theme.spacing.unit * 3,
        '& > *:not(:last-child)': {
            marginBottom: theme.spacing.unit * 3,
        },
    },
    stepBox: {
        borderRadius: theme.spacing.unit,
        padding: theme.spacing.unit * 2,
        marginBottom: 0,
        display: 'flex',
        flexDirection: 'column',
    },
    blueStep: {
        backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        border: `1px solid ${COLOURS.LIGHT_BLUE_BORDER}`,
    },
    purpleStep: {
        backgroundColor: COLOURS.LIGHT_PURPLE_BG,
        border: `1px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
    },
    greenStep: {
        backgroundColor: COLOURS.LIGHT_GREEN,
        border: `1px solid ${COLOURS.LIGHT_GREEN_BORDER}`,
    },
    amberStep: {
        background: `linear-gradient(135deg, ${COLOURS.LIGHT_AMBER} 0%, ${COLOURS.LIGHT_AMBER_2} 100%)`,
        border: `4px solid ${COLOURS.AMBER}`,
        boxShadow: '0 4px 12px rgba(255, 193, 7, 0.3)',
    },
    stepNumber: {
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: COLOURS.WHITE,
        fontWeight: 600,
        fontSize: 18,
        marginRight: theme.spacing.unit * 1.5,
        flexShrink: 0,
    },
    blueNumber: {
        backgroundColor: COLOURS.MATERIAL_BLUE,
    },
    purpleNumber: {
        backgroundColor: COLOURS.MATERIAL_PURPLE,
    },
    greenNumber: {
        backgroundColor: COLOURS.MATERIAL_GREEN,
    },
    amberNumber: {
        background: `linear-gradient(135deg, ${COLOURS.ORANGE} 0%, ${COLOURS.AMBER_YELLOW} 100%)`,
        boxShadow: '0 2px 8px rgba(245, 124, 0, 0.4)',
    },
    stepHeader: {
        display: 'flex',
        alignItems: 'flex-start',
        marginBottom: theme.spacing.unit * 1.5,
    },
    stepTitle: {
        fontSize: 24,
        fontWeight: 600,
        marginBottom: theme.spacing.unit * 0.5,
    },
    stepText: {
        fontSize: 18,
        lineHeight: 1.6,
    },
    bulletPoint: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: theme.spacing.unit,
    },
    bullet: {
        width: 6,
        height: 6,
        borderRadius: '50%',
        marginRight: theme.spacing.unit,
        flexShrink: 0,
    },
    blueBullet: {
        backgroundColor: COLOURS.MATERIAL_BLUE,
    },
    examplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: 'auto',
        paddingTop: theme.spacing.unit * 2,
        justifyContent: 'flex-start',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
    },
    exampleItem: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: 80,
        justifyContent: 'flex-start',
    },
    exampleImage: {
        width: 64,
        height: 64,
        objectFit: 'cover',
        borderRadius: theme.spacing.unit,
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'all 0.2s',
        '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
        },
    },
    purpleBorder: {
        border: `2px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
    },
    greenBorder: {
        border: `2px solid ${COLOURS.LIGHT_GREEN_BORDER}`,
    },
    exampleLabel: {
        fontSize: 14,
        textAlign: 'center',
        marginTop: theme.spacing.unit,
        fontWeight: 700,
        lineHeight: 1.2,
    },
    purpleLabel: {
        color: COLOURS.PURPLE_TEXT,
    },
    greenLabel: {
        color: COLOURS.GREEN_TEXT,
    },
    noteBox: {
        backgroundColor: COLOURS.NOTE_GREEN,
        padding: theme.spacing.unit * 1.5,
        borderRadius: theme.spacing.unit,
        marginTop: theme.spacing.unit,
    },
    maxValueBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: COLOURS.DARK_AMBER,
        color: COLOURS.WHITE,
        padding: '6px 12px',
        borderRadius: 20,
        fontSize: 18,
        fontWeight: 700,
        marginBottom: theme.spacing.unit * 1.5,
        boxShadow: '0 2px 6px rgba(255, 160, 0, 0.4)',
    },
    warningBox: {
        backgroundColor: COLOURS.LIGHT_GREY,
        padding: theme.spacing.unit * 1.5,
        borderRadius: theme.spacing.unit,
        display: 'flex',
        alignItems: 'center',
    },
    warningIcon: {
        color: COLOURS.MATERIAL_RED,
        marginRight: theme.spacing.unit,
        fontSize: 16,
        flexShrink: 0,
    },
    link: {
        color: COLOURS.MATERIAL_BLUE,
        textDecoration: 'none',
        fontWeight: 500,
        '&:hover': {
            textDecoration: 'underline',
        },
    },
    dialogImage: {
        width: '100%',
        height: 'auto',
        maxHeight: '80vh',
        objectFit: 'contain',
    },
    closeButton: {
        position: 'absolute',
        right: theme.spacing.unit,
        top: theme.spacing.unit,
        color: theme.palette.grey[500],
    },
    twoColumnGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        columnGap: theme.spacing.unit * 3,
        rowGap: theme.spacing.unit * 2,
        [theme.breakpoints.down('sm')]: {
            gridTemplateColumns: '1fr',
        },
    },
});

const ImageDialog = ({ open, onClose, image, alt, classes }) => (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <IconButton className={classes.closeButton} onClick={onClose}>
            <CloseIcon />
        </IconButton>
        <DialogContent>
            <img src={image} alt={alt} className={classes.dialogImage} />
        </DialogContent>
    </Dialog>
);

ImageDialog.propTypes = {
    open: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    image: PropTypes.string.isRequired,
    alt: PropTypes.string.isRequired,
    classes: PropTypes.object.isRequired,
};

const ExampleImage = ({
    src,
    alt,
    label,
    borderClass,
    labelColorClass,
    classes,
}) => {
    const [dialogOpen, setDialogOpen] = useState(false);

    return (
        <div className={classes.exampleItem}>
            <button
                type="button"
                onClick={() => setDialogOpen(true)}
                style={{
                    border: 'none',
                    background: 'none',
                    padding: 0,
                    cursor: 'pointer',
                }}
                aria-label={`View example: ${alt}`}
            >
                <img
                    src={src}
                    alt={alt}
                    className={`${classes.exampleImage} ${classes[borderClass]}`}
                />
            </button>
            <Typography
                className={`${classes.exampleLabel} ${classes[labelColorClass]}`}
                color="textSecondary"
            >
                {label}
            </Typography>
            <ImageDialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                image={src}
                alt={alt}
                classes={classes}
            />
        </div>
    );
};

ExampleImage.propTypes = {
    src: PropTypes.string.isRequired,
    alt: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    borderClass: PropTypes.string.isRequired,
    labelColorClass: PropTypes.string.isRequired,
    classes: PropTypes.object.isRequired,
};

const ClaimInfoSection = ({ classes }) => (
    <div className={classes.root}>
        <div className={`${classes.stepBox} ${classes.blueStep}`}>
            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.blueNumber}`}>
                    1
                </div>
                <div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: COLOURS.DARK_BLUE }}
                    >
                        Confirm Your Eligibility
                    </Typography>
                    <div>
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
                        classes={classes}
                    />
                    <ExampleImage
                        src={employmentLetterExample}
                        alt="Example employment letter"
                        label="Employment Letter"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={businessCardExample}
                        alt="Example business card"
                        label="Business Card"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                        classes={classes}
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
                        classes={classes}
                    />
                    <ExampleImage
                        src={businessLicenseExample}
                        alt="Example business license"
                        label="Business License"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={utilityBillExample}
                        alt="Example utility bill"
                        label="Utility Bill"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                        classes={classes}
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
                    <strong style={{ fontSize: 20 }}>Get Verified:</strong>{' '}
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
    </div>
);

ClaimInfoSection.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(claimInfoStyles)(ClaimInfoSection);
