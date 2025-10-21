import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import ImageDialog from './ImageDialog';
import { claimInfoStyles } from './styles';

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

export default withStyles(claimInfoStyles)(ExampleImage);
